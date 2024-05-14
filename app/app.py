import asyncio
import os
import subprocess
import time
from datetime import datetime

import cv2
from camera import generate_frames, model, threshold
from database.scripts.light import fetch_light_state, update_light_state
from database.scripts.sensor import insert_sensor_data
from dotenv import load_dotenv
from flask import Flask, Response, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from local_inference import query
from myMqtt import *
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/socket.io/*": {"origins": "*"},
        r"/light/*": {"origins": "*"},
        r"/light_state/*": {"origins": "*"},
        r"/audio/*": {"origins": "*"},
        r"/light_sys/*": {"origins": "*"},
    },
)
connection_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@localhost:27017/"
socketio = SocketIO(app, cors_allowed_origins="*")
db = {
    "camera_streams": [0, "http://192.168.1.36:8080/video"],
    "light_sys": {
        "bedroom": ["light1", "light2", "light3", "light4", "light5"],
        "kitchen": ["light1", "light2", "light3", "light4", "light5"],
        "livingroom": ["light1", "light2", "light3", "light4", "light5"],
    },
}


def debounce(wait):
    # Decorator that will postpone a function's
    # execution until after `wait` seconds
    # have elapsed since the last time it was invoked.
    def decorator(fn):
        last_invoked = {}

        def debounced(stream_link, *args, **kwargs):
            nonlocal last_invoked
            now = time.time()
            if (
                stream_link not in last_invoked
                or now - last_invoked[stream_link] >= wait
            ):
                last_invoked[stream_link] = now
                return fn(stream_link, *args, **kwargs)

        return debounced

    return decorator


@debounce(1.0)
def send_notification(message):
    socketio.emit("notification", {"message": message})


async def only_detect_box(stream_link):
    stream = cv2.VideoCapture(stream_link)
    while True:
        success, frame = stream.read()
        if not success:
            break
        else:
            b_boxes = model(frame, verbose=False)[0].boxes.data.tolist()
            count = 0
            for b_box in b_boxes:
                x1, y1, x2, y2, score, class_id = b_box
                if score > threshold:
                    count += 1
            if count > 1:
                message = (
                    f"{stream_link} currently has {count} numbers of people in the view"
                )
                send_notification(stream_link, message)
        await asyncio.sleep(0)  # Yield control to the event loop


@app.before_first_request
def start_detection_task():
    for stream_link in db["camera_streams"]:
        asyncio.create_task(only_detect_box(stream_link))


@socketio.on("connect")
def test_connect():
    emit("notification", {"message": "New notification!"})
    for i in range(3):
        test_message = "New notification! " + str(i)
        emit("notification", {"message": test_message})


@socketio.on("disconnect")
def test_disconnect():
    print("Client disconnected")


@app.route("/audio", methods=["POST"])
async def receive_audio():
    if "file" not in request.files:
        return "No file part in the request.", 400

    file = request.files["file"]

    if file.filename == "":
        return "No selected file.", 400

    if file:
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)
        response = await query(filepath)
        if "error" in response:
            print(f"Error: {response}, Details: {response['details']}")
            return response, 500
        return response, 200


@app.route("/light/sys", methods=["GET"])
def get_light_system():
    mongo_client = MongoClient(connection_string)
    iot_db = mongo_client.iot_232
    light_collection = iot_db["light"]

    result = {}
    all_data = light_collection.find({})

    for data in all_data:
        for room, lights in data.items():
            if room != "_id":
                result[room] = [light["name"] for light in lights]

    return result, 200


@app.route("/light/control", methods=["POST"])
def light_switch():
    mongo_client = MongoClient(connection_string)
    iot_db = mongo_client.iot_232
    light_collection = iot_db["light"]

    room = request.json.get("room")
    light_id = request.json.get("light_id")
    state = request.json.get("state")
    print(request.json)

    valid_states = ["ON", "OFF"]

    if state not in valid_states:
        return {"error": "Invalid state"}, 400

    room_data = light_collection.find_one({room: {"$exists": True}})
    if room_data is None:
        return {"error": "Invalid room"}, 400

    light_names = [light["name"] for light in room_data[room]]
    if light_id not in light_names:
        return {"error": "Invalid light_id for the given room"}, 400

    light_index = light_names.index(light_id)

    client.publish(
        topic=topic_head + "led-slash-" + room,
        payload=f"{room} {light_index} {state}",
    )
    update_light_state(room, light_id, state)

    return {"room": room, "light_id": light_id, "state": state}, 200


@app.route("/light/state", methods=["GET"])
def get_light_state():
    room = request.args.get("room")
    light_id = request.args.get("light_id")

    state = fetch_light_state(room, light_id)
    if state is None:
        return {"error": "wrong room or light id"}, 400

    return {"state": state}, 200


@app.route("/video_feed/<int:id>")
def video_feed(id):
    if id < 0 or id >= len(db["camera_streams"]):
        return "Invalid camera ID", 400

    stream_link = db["camera_streams"][id]

    return Response(
        generate_frames(stream_link),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/")
def index():
    return "Hello"


def getTopicName(name: str) -> str:
    return topic_head + name


def on_message(client, userdata, message):
    if message.topic == getTopicName("led-slash-bedroom"):
        print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
    if message.topic == getTopicName("led-slash-livingroom"):
        print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
    if message.topic == getTopicName("led-slash-kitchen"):
        print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
    if message.topic == getTopicName("sensor-temperature"):
        insert_sensor_data(
            sensor_id="temp1",
            type="temp",
            value=int(message.payload.decode()),
            timestamp=datetime.now(),
        )
    if message.topic == getTopicName("sensor-moisture"):
        insert_sensor_data(
            sensor_id="moist1",
            type="moist",
            value=int(message.payload.decode()),
            timestamp=datetime.now(),
        )


if __name__ == "__main__":
    mongo_client = MongoClient(connection_string)
    iot_db = mongo_client.iot_232

    sensor_collection = iot_db["sensor_data"]
    led_collection = iot_db["light"]

    client = connect_mqtt()
    client.subscribe(f"{topic_head}#")
    client.on_message = on_message
    client.loop_start()
    app.run(host="0.0.0.0", port=os.environ.get("FLASK_PORT"))
    client.loop_stop()
