import os
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
connection_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@localhost:27017/"

camera_streams_data = [
    {"id": 0, "stream_link": 0},
    {"id": 1, "stream_link": "http://192.168.1.36:8080/video"},
    # Add more camera streams as needed
]

if __name__ == "__main__":
    mongo_client = MongoClient(connection_string)
    iot_db = mongo_client.iot_232
    camera_collection = iot_db["camera"]

    if camera_collection.count_documents({}) > 0:
        print("Data already exists in the collection. Exiting...")
    else:
        for data in camera_streams_data:
            camera_collection.insert_one(data)
