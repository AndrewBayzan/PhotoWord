from flask import Flask, Blueprint
from app.extensions import db, migrate
from app.models import Users, Words


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    from .blueprints.main import main
    from .blueprints.register import auth
    from .blueprints.dict import dict_bp
    from .blueprints.tests import tests_bp

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(dict_bp)
    app.register_blueprint(tests_bp, url_prefix="/tests")


    return app   


