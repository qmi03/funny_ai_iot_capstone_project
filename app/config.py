# config.py
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", False)
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
