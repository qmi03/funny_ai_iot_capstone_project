import os
from datetime import datetime

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
connection_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@localhost:27017/"

rooms = ["bedroom", "livingroom", "kitchen"]
lights_per_room = 5


def create_light_data(room, light_id):
    return {
        "name": f"light{light_id}",
        "state": True,  # Light is on
        "last_changed": datetime.now().isoformat(),
        "uptime_records": [],
    }


if __name__ == "__main__":
    mongo_client = MongoClient(connection_string)
    iot_db = mongo_client.iot_232
    light_collection = iot_db["light"]

    if light_collection.count_documents({}) > 0:
        print("Data already exists in the collection. Exiting...")
    else:
        for room in rooms:
            room_data = []
            for light_id in range(1, lights_per_room + 1):
                room_data.append(create_light_data(room, light_id))
            light_collection.insert_one({room: room_data})
