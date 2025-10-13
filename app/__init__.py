from flask import Flask
from .extensions import db, bcrypt, login_manager
from .routes.auth import auth_bp
from .routes.home import home_bp
from .routes.dashboard import dashboard_bp


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(home_bp)

    with app.app_context():
        db.create_all()

    return app
