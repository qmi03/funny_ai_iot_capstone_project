import cv2


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
