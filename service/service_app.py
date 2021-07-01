from flask import Flask
from service.service import flask_service

def create_app():
    app = Flask("simon-iot")
    app.register_blueprint(service)
    return app
