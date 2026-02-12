from flask import Flask
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise RuntimeError("MONGO_URI is missing. Check your .env file.")

client = MongoClient(
    mongo_uri,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=8000,
)

@app.route("/")
def home():
    return "Server is running"

@app.route("/test-connection")
def test_connection():
    try:
        client.admin.command("ping")
        return "Mongo ping OK"
    except PyMongoError as e:
        return f"Mongo error: {e}", 500
