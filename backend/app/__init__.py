from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint
from config import config

db = SQLAlchemy()
api = Api()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    CORS(app)
    
    # Configurar Swagger
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.yml'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Carbon Footprint API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Registrar blueprints
    from .routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Redirecionar a raiz para o Swagger
    @app.route('/')
    def index():
        return redirect(SWAGGER_URL)
    
    return app 