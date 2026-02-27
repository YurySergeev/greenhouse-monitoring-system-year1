from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS

from app.api.routes import api_bp
from app.extensions import init_extensions

def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    init_extensions(app)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/")
    def home():
        return {"message": "Greenhouse Backend Running"}

    return app