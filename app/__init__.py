from flask import Flask, Blueprint
from app.extensions import db
from app.models import Users


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    from .blueprints.main import main
    from .blueprints.register import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    # with app.app_context():
    return app   


