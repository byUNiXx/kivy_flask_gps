import os

from flask import Flask

from extensions import db, migrate
from routes.alarm import alarm_routes
from routes.index import index
from routes.phone import phone
from routes.phone_alarm import phone_alarm_routes


# Factoria de app

def create_app(config="src/config/config.py"):
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    app.config.from_pyfile(os.path.join(basedir, config))
    app.url_map.strict_slashes = False
    register_extensions(app)
    init_database(app)
    register_blueprints(app)
    return app


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    return None


def register_blueprints(app):
    app.register_blueprint(index)
    app.register_blueprint(phone)
    app.register_blueprint(alarm_routes)
    app.register_blueprint(phone_alarm_routes)
    return None


def init_database(app):
    with app.app_context():
        db.create_all()
    return None


if __name__ == '__main__':
    create_app().run()
