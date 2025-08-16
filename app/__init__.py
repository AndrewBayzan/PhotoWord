from flask import Flask, Blueprint
from app.extensions import db, migrate
from app.models import Users


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    from .blueprints.main import main
    from .blueprints.register import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)



    return app   


