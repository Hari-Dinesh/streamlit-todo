import hashlib
import pymongo
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import os


if os.getenv("DB_URL"):
    # Use environment variable (for local development)
    mongo_url = os.getenv("DB_URL")
else:
    # Use Streamlit secrets (for Streamlit Cloud)
    mongo_url = st.secrets["db_url"]
client = pymongo.MongoClient(mongo_url)
db = client["task_manager"]
users_collection = db["users"]
tasks_collection = db["tasks"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hashed == hash_password(password)
