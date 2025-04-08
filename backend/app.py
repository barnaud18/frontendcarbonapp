import os
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///carbonfootprint.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Enable CORS
CORS(app)

# Initialize the app with the extension
db.init_app(app)

# Configure Swagger
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Calculadora de Pegada de Carbono Agrícola API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Import routes after app is created to avoid circular imports
from backend.routes import *

# Create database tables
with app.app_context():
    db.create_all()
