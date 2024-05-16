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
                "metadata": {"sensorId": sensor_id, "type": sensor_type},
                "timestamp": timestamp,
                "value": value,
            }
        )
    finally:
        mongo_client.close()


if __name__ == "__main__":
    # Example usage:
    timestamp = datetime(2024, 5, 15, 12, 0, 0)  # Create a datetime object
    asyncio.run(insert_sensor_data("sensor123", "temperature", 25.5, timestamp))
