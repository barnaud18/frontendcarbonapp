from flask import Flask
from flask_cors import CORS
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    CORS(app)
    
    # Registrar blueprints
    from .routes import views_bp
    app.register_blueprint(views_bp)
    
    return app 