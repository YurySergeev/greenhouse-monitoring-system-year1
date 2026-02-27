from flask import Blueprint
from app.db.mongo import get_db

api_bp = Blueprint("api", __name__)

@api_bp.get("/test")
def test():
    return {"status": "API working"}

@api_bp.get("/weather/latest")
def latest_weather():
    db = get_db()
    doc = db["daily_weather"].find_one(sort=[("day", -1)], projection={"_id": 0})
    return doc or {}