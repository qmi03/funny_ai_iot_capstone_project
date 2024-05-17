import asyncio

import cv2
from ultralytics import YOLO

weight_path = "ai/cv/model.pt"
model = YOLO(weight_path)
threshold = 0.5


async def generate_frames(stream_link, show_count_and_bounding_box=True):
    stream = cv2.VideoCapture(stream_link)
    while True:
        success, frame = stream.read()
        if not success:
            break
        else:
            if show_count_and_bounding_box:
                bboxes = model(frame, verbose=False)[0].boxes.data.tolist()
                count = 0
                for bbox in bboxes:
                    x1, y1, x2, y2, score, class_id = bbox
                    if score > threshold:
                        count += 1
                        cv2.rectangle(
                            frame,
                            (int(x1), int(y1)),
                            (int(x2), int(y2)),
                            (255, 0, 255),
                            2,
                        )
                    # pos = (50, 50)
                    cv2.putText(
                        frame,
                        f"Number of face: {count}",
                        (20, (frame.shape[0] - 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA,
                    )
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpg\r\n\r\n" + frame + b"\r\n")
        await asyncio.sleep(0)  # Allow other tasks to run
