import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()
connection_string = f"mongodb://{os.environ.get('MONGO_USER')}:{os.environ.get('MONGO_PASSWORD')}@localhost:27017/"


async def update_light_state(room, light_id, state):
    mongo_client = AsyncIOMotorClient(connection_string)
    try:
        iot_db = mongo_client.iot_232
        light_collection = iot_db["light"]

        room_data = await light_collection.find_one({room: {"$exists": True}})
        if room_data is not None:
            for light in room_data[room]:
                if light["name"] == light_id:
                    # Convert the state parameter to a boolean
                    state_bool = True if state == "ON" else False

                    # If the current state is already the same as the requested state, return
                    if light["state"] == state_bool:
                        return

                    # Update the state and last_changed fields
                    light["state"] = state_bool
                    old_last_changed = light["last_changed"]
                    light["last_changed"] = datetime.now().isoformat()

                    # If the light is being turned off, add a new uptime record
                    if state == "OFF":
                        light["uptime_records"].append(
                            {
                                "start": old_last_changed,
                                "end": light["last_changed"],
                            }
                        )

                    # Update the document in the database
                    await light_collection.update_one(
                        {room: {"$exists": True}}, {"$set": {room: room_data[room]}}
                    )
                    return

        raise ValueError(
            f"The room '{room}' or the light '{light_id}' does not exist in the database."
        )
    finally:
        mongo_client.close()


async def fetch_light_state(room, light_id):
    mongo_client = AsyncIOMotorClient(connection_string)
    try:
        iot_db = mongo_client.iot_232
        light_collection = iot_db["light"]

        room_data = await light_collection.find_one({room: {"$exists": True}})
        if room_data is not None:
            for light in room_data[room]:
                if light["name"] == light_id:
                    return light["state"]

        return None
    finally:
        mongo_client.close()


if __name__ == "__main__":
    asyncio.run(update_light_state("livingroom", "light3", "OFF"))
