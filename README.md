# funny_ai_iot_capstone_project

# About
This is a smarthome school project. Has some iot and ai.
# Requirements

1. node
2. python
3. docker compose

# Run
## Backend + Database
1. `docker compose up` or `docker-compose up` (whatever works for you)
2. `cd app`
3. Create a virtual environment if needed, then `pip install -r requirements.txt`
4. Create the .env file from .env.example. And fill in the fields.
5. Run backend: `python app.py`
6. Initialize the rooms in the database: `python database/scripts/init_light.py`
## Frontend
1. `cd smarthome`
2. Install dependencies, use: `yarn` or `npm install`.
3. Create the .env file from .env.example. And fill in the fields.
4. Run the frontend: `yarn dev` (add `--host` to expose ip).
