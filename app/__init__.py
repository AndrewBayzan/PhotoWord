from flask import Flask, Blueprint
from app.extensions import db
from app.models import Users


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    from .blueprints.main import main

    app.register_blueprint(main)

    # with app.app_context():
    return app   


