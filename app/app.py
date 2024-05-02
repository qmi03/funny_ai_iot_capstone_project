import os

import cv2
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://192.168.1.20:5173"])

camera_streams = [
    0,
]


def fetch_light_state(room, light_id):
    return True


@app.route("/light", methods=["POST"])
def light_switch():
    room = request.json.get("room")
    light_id = request.json.get("light_id")
    state = request.json.get("state")

    if state not in ["ON", "OFF"]:
        return {"error": "Invalid state"}, 400

    if room == "living room" and light_id == "1":
        if state == "ON":
            print(room, light_id, state)
        else:
            print(room, light_id, state)

    return {"room": room, "light_id": light_id, "state": state}, 200


@app.route("/light_state", methods=["GET"])
def get_light_state():
    room = request.args.get("room")
    light_id = request.args.get("light_id")

    state = fetch_light_state(room, light_id)

    return {"state": state}, 200


def generate_frames(stream_link):
    stream = cv2.VideoCapture(stream_link)
    while True:
        success, frame = stream.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".png", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/png\r\n\r\n" + frame + b"\r\n")


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
    app.run(host="0.0.0.0", port=8000)
