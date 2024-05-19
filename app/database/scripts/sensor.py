import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
connection_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@localhost:27017/"


async def insert_sensor_data(sensor_id, sensor_type, value, timestamp):
    mongo_client = AsyncIOMotorClient(connection_string)
    try:
        iot_db = mongo_client.iot_232
        sensor_collection = iot_db["sensor_data"]

        await sensor_collection.insert_one(
            {
                "metadata": {"sensor_id": sensor_id, "type": sensor_type},
                "timestamp": timestamp,
                "value": value,
            }
        )
    finally:
        mongo_client.close()


async def get_latest_data(sensor_id):
    mongo_client = AsyncIOMotorClient(connection_string)
    try:
        iot_db = mongo_client.iot_232
        sensor_collection = iot_db["sensor_data"]

        # We sort by timestamp in descending order and get the first document
        document = await sensor_collection.find_one(
            {"metadata.sensor_id": sensor_id}, sort=[("timestamp", -1)]
        )

        if document is not None:
            value = document.get("value")
            return value
        else:
            return None
    finally:
        mongo_client.close()


if __name__ == "__main__":
    # Example usage:
    timestamp = datetime(2024, 5, 15, 12, 0, 0)  # Create a datetime object
    asyncio.run((get_latest_data("temp1")))
