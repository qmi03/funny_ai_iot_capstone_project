import asyncio
import json
import logging
import os
import random
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiomqtt
from database.scripts.sensor import insert_sensor_data
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from utils.convert import *
from utils.mqtt import *
from utils.voice_commands import *

load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler(),  # Also log to the console
    ],
)

# Get a logger instance
logger = logging.getLogger(__name__)


connection_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@localhost:27017/"
motor_client = AsyncIOMotorClient(connection_string)
db = motor_client["iot_232"]

# Define collections
sensor_collection = db["sensor_data"]
os.makedirs("uploads", exist_ok=True)

mqtt_client = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(json.dumps({"message": message}))


class TaskManager:
    def __init__(self):
        self.tasks: Dict[int, asyncio.Task] = {}

    def add_task(self, stream_id: int, task: asyncio.Task):
        self.tasks[stream_id] = task

    def get_task(self, stream_id: int) -> Optional[asyncio.Task]:
        return self.tasks.get(stream_id)

    def remove_task(self, stream_id: int):
        if stream_id in self.tasks:
            del self.tasks[stream_id]


task_manager = TaskManager()

connection_manager = ConnectionManager()


def getTopicName(topic: str):
    return topic_head + topic


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
            data = {
                "sensor_id": "temp1",
                "sensor_type": "temp",
                "value": int(message.payload.decode()),
                "timestamp": datetime.now().isoformat(),
            }
            await connection_manager.send_message(json.dumps(data))

            try:
                await insert_sensor_data(
                    sensor_id=data["sensor_id"],
                    sensor_type=data["sensor_type"],
                    value=data["value"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                )
            except Exception as e:
                print(f"Error inserting sensor data: {e}")
        if message.topic.matches(getTopicName("sensor-moisture")):
            print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
            data = {
                "sensor_id": "moist1",
                "sensor_type": "moist",
                "value": int(message.payload.decode()),
                "timestamp": datetime.now().isoformat(),
            }
            await connection_manager.send_message(json.dumps(data))

            try:
                await insert_sensor_data(
                    sensor_id=data["sensor_id"],
                    sensor_type=data["sensor_type"],
                    value=data["value"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                )
            except Exception as e:
                print(f"Error inserting sensor data: {e}")


@asynccontextmanager
async def lifespan(app):
    global mqtt_client
    interval = 5  # Seconds
    while True:
        try:
            async with aiomqtt.Client(
                identifier=f"python-mqtt-{random.randint(0, 1000)}",
                hostname=mqtt_host,
                port=mqtt_port,
                username=mqtt_username,
                password=mqtt_password,
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
        except aiomqtt.MqttError:
            logger.info(f"Connection lost; Reconnecting in {interval} seconds ...")
            await asyncio.sleep(interval)


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)


async def send_message(message):
    await connection_manager.send_message(message)


@app.get("/")
async def index():
    return {"message": "Hello"}


@app.get("/sensor/data/history")
async def get_history_data(sensor_id: str, hours: int = 24):
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        cursor = sensor_collection.find(
            {
                "metadata.sensor_id": sensor_id,
                "timestamp": {"$gte": start_time, "$lte": end_time},
            }
        )
        sensor_data = await cursor.to_list(length=None)
        sensor_data = convert_objectid(sensor_data)
        sensor_data = [
            {
                "sensor_id": data["metadata"]["sensor_id"],
                "sensor_type": data["metadata"]["type"],
                "value": data["value"],
                "timestamp": data["timestamp"],
            }
            for data in sensor_data
        ]
        print(sensor_data)
        return sensor_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching historical data: {str(e)}"
        )


@app.get("/sensor/ids")
async def get_sensor_ids():
    try:
        sensor_ids = await sensor_collection.distinct("metadata.sensor_id")
        return sensor_ids
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching sensor IDs: {str(e)}"
        )
