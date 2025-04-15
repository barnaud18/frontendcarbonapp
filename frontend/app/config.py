import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    BACKEND_URL = os.environ.get('BACKEND_URL') or 'http://localhost:5000'
    SWAGGER_URL = os.environ.get('SWAGGER_URL') or 'http://localhost:5000/api/docs' 