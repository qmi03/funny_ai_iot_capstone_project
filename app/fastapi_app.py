import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime

import aiomqtt
from camera import generate_frames
from database.scripts import light
from database.scripts.sensor import insert_sensor_data
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from local_inference import query
from motor.motor_asyncio import AsyncIOMotorClient
from myMqtt import *
from pydantic import BaseModel

load_dotenv()

# Create an asyncio Queue for message passing
message_queue = asyncio.Queue()

connection_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@localhost:27017/"
motor_client = AsyncIOMotorClient(connection_string)
db = motor_client["iot_232"]

# Define collections
sensor_collection = db["sensor_data"]
light_collection = db["light"]
camera_collection = db["camera"]
# Replace your existing route decorators with FastAPI's equivalents
os.makedirs("uploads", exist_ok=True)


mqtt_client = None


async def listen(client):
    async for message in client.messages:

        if message.topic.matches(getTopicName("led-slash-bedroom")):
            print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
        if message.topic == getTopicName("led-slash-livingroom"):
            print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
        if message.topic.matches(getTopicName("led-slash-kitchen")):
            print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
        if message.topic.matches(getTopicName("sensor-temperature")):
            print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
            try:
                await insert_sensor_data(
                    sensor_id="temp1",
                    sensor_type="temp",
                    value=int(message.payload.decode()),
                    timestamp=datetime.now(),
                )
            except Exception as e:
                print(f"Error inserting sensor data: {e}")
        if message.topic.matches(getTopicName("sensor-moisture")):
            print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
            try:
                await insert_sensor_data(
                    sensor_id="moist1",
                    sensor_type="moist",
                    value=int(message.payload.decode()),
                    timestamp=datetime.now(),
                )
            except Exception as e:
                print(f"Error inserting sensor data: {e}")


@asynccontextmanager
async def lifespan(app):
    global mqtt_client
    async with aiomqtt.Client(
        identifier=f"python-mqtt-{random.randint(0, 1000)}",
        hostname=host,
        port=port,
        username=username,
        password=password,
    ) as c:
        mqtt_client = c
        await mqtt_client.subscribe(f"{topic_head}#")
        loop = asyncio.get_event_loop()
        task = loop.create_task(listen(mqtt_client))
        yield
        # Cancel the task
        task.cancel()
        # Wait for the task to be cancelled
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


async def get_stream_link_from_db(id: int):
    stream_info = await camera_collection.find_one({"id": id})
    if stream_info:
        return stream_info.get("stream_link")
    else:
        return None


@app.post("/audio")
async def receive_audio(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        filepath = os.path.join("uploads", file.filename)
        with open(filepath, "wb") as f:
            f.write(file.file.read())

        # Process the uploaded audio file
        response = await query(filepath)

        # Check for processing errors
        if "error" in response:
            error_message = response["error"]
            raise HTTPException(status_code=500, detail=error_message)

        return JSONResponse(content=response, status_code=200)
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        error_message = f"Error processing audio: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)


@app.get("/video_feed/{id}")
async def video_feed(id: int):
    stream_link = await get_stream_link_from_db(id)
    if stream_link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid camera ID"
        )

    async def frames():
        async for frame in generate_frames(stream_link):
            yield frame

    return StreamingResponse(
        frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/")
async def index():
    return {"message": "Hello"}


@app.get("/light/sys")
async def get_light_system():
    try:
        result = {}
        async for data in light_collection.find({}):
            for room, lights in data.items():
                if room != "_id":
                    result[room] = [light["name"] for light in lights]

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching light system data: {str(e)}"
        )


async def get_light_index(room: str, light_id: str):
    room_data = await light_collection.find_one({room: {"$exists": True}})
    if room_data is None:
        raise HTTPException(status_code=400, detail="Invalid room")

    light_names = [light["name"] for light in room_data[room]]
    if light_id not in light_names:
        raise HTTPException(
            status_code=400, detail="Invalid light_id for the given room"
        )

    return light_names.index(light_id)


class LightControlRequest(BaseModel):
    room: str
    light_id: str
    state: str


@app.post("/light/control")
async def light_switch(request_body: LightControlRequest):
    # Extract parameters from the request body
    room = request_body.room
    light_id = request_body.light_id
    state = request_body.state

    if state not in ["ON", "OFF"]:
        raise HTTPException(status_code=400, detail="Invalid state")

    # Get the index of the light in the room
    light_index = await get_light_index(room, light_id)

    # Publish MQTT message
    mqtt_client.publish(
        topic=topic_head + "led-slash-" + room,
        payload=f"{room} {light_index} {state}",
    )

    await light.update_light_state(room, light_id, state)

    return {"room": room, "light_id": light_id, "state": state}


@app.get("/light/state")
async def get_light_state(room: str, light_id: str):
    # Fetch light state from MongoDB
    state = await light.fetch_light_state(room, light_id)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid room or light ID"
        )
    return {"state": state}
