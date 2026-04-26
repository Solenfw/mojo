from flask import Flask
from app.core.database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.core.config.Config")

    db.init_app(app)

    from app.modules.user.controller import user_bp
    app.register_blueprint(user_bp)

    return app
