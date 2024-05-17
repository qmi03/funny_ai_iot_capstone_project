import os

from dotenv import load_dotenv

load_dotenv()


mqtt_host = os.getenv("MQTT_HOST")
mqtt_port = int(os.getenv("MQTT_PORT"))
mqtt_username = os.getenv("ADAFRUIT_USER")
mqtt_password = os.getenv("ADAFRUIT_KEY")

topic_head = f"{mqtt_username}/feeds/"


def getTopicName(name: str) -> str:
    return topic_head + name
