import os
import time

from camera import generate_frames
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from light import fetch_light_state
from myMqtt import *

load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/socket.io/*": {"origins": "*"},
        r"/light/*": {"origins": "*"},
        r"/light_state/*": {"origins": "*"},
    },
)

camera_streams = [
    0,
    "http://192.168.1.36:8080/video"
]

socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on("connect")
def test_connect():
    emit("notification", {"message": "New notification!"})
    for i in range(3):
        test_message = "New notification! " + str(i)
        emit("notification", {"message": test_message})


@socketio.on("disconnect")
def test_disconnect():
    print("Client disconnected")


@app.route("/light", methods=["POST"])
def light_switch():
    room = request.json.get("room")
    light_id = request.json.get("light_id")
    state = request.json.get("state")

    if state not in ["ON", "OFF"]:
        return {"error": "Invalid state"}, 400

    if (room == "livingroom" or room == "bedroom" or room == "kitchen") and (light_id == "5" or light_id == "1" or light_id == "2" or light_id == "3" or light_id == "4") :
        client.publish(topic=topic_head+"led-slash-bedroom", payload=room + " " + light_id + " " + state)
    return {"room": room, "light_id": light_id, "state": state}, 200


@app.route("/light_state", methods=["GET"])
def get_light_state():
    room = request.args.get("room")
    light_id = request.args.get("light_id")

    state = fetch_light_state(room, light_id)

    return {"state": state}, 200


@app.route("/video_feed/<int:id>")
def video_feed(id):
    if id < 0 or id >= len(camera_streams):
        return "Invalid camera ID", 400

    stream_link = camera_streams[id]

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
    # client.publish(topic=topic_head+"led-slash-bedroom", payload="livingroom" + " " + "1" + " " + "ON")
    app.run(host="0.0.0.0", port=8000)
