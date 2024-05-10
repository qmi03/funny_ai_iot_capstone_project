import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
connection_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@localhost:27017/"


def insert_sensor_data(sensor_id, type, value, timestamp):
    mongo_client = MongoClient(connection_string)
    iot_db = mongo_client.iot_232
    sensor_collection = iot_db["sensor_data"]

    sensor_collection.insert_one(
        {
            "metadata": {"sensorId": sensor_id, "type": type},
            "timestamp": timestamp,
            "value": value,
        }
    )


if __name__ == "__main__":
    pass
