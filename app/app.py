import asyncio
import os
import subprocess
import time

from camera import generate_frames
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from inference import query
from light import fetch_light_state
from myMqtt import *
from werkzeug.utils import secure_filename

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


socketio = SocketIO(app, cors_allowed_origins="*")
db = {
    "camera_streams": [0, "http://192.168.1.36:8080/video"],
    "light_sys": {
        "bedroom": ["light1", "light2", "light3", "light4", "light5"],
        "kitchen": ["light1", "light2", "light3", "light4", "light5"],
        "livingroom": ["light1", "light2", "light3", "light4", "light5"],
    },
}


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
        filename = secure_filename(file.filename)
        filepath = os.path.join("uploads", filename)
        file.save(filepath)
        response = await query(filepath)
        if "error" in response:
            print(f"Error: {response['error']}, Details: {response['details']}")
            return response, 500
        return response, 200


@app.route("/light/sys", methods=["GET"])
def get_light_system():
    return db["light_sys"], 200


@app.route("/light/control", methods=["POST"])
def light_switch():
    room = request.json.get("room")
    light_id = request.json.get("light_id")
    state = request.json.get("state")
    print(request.json)
    valid_rooms = db["light_sys"].keys()
    valid_states = ["ON", "OFF"]

    if state not in valid_states:
        return {"error": "Invalid state"}, 400

    if room not in valid_rooms:
        return {"error": "Invalid room"}, 400

    if light_id not in db["light_sys"][room]:
        return {"error": "Invalid light_id for the given room"}, 400

    light_index = db["light_sys"][room].index(light_id)

    client.publish(
        topic=topic_head + "led-slash-" + room,
        payload=f"{room} {light_index} {state}",
    )

    return {"room": room, "light_id": light_id, "state": state}, 200


@app.route("/light/state", methods=["GET"])
def get_light_state():
    room = request.args.get("room")
    light_id = request.args.get("light_id")

    state = fetch_light_state(room, light_id)

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


if __name__ == "__main__":
    client = connect_mqtt()
    client.loop_start()
    app.run(host="0.0.0.0", port=os.environ.get("FLASK_PORT"))
