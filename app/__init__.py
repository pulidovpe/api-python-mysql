from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('APP_SECRET')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_DATABASE')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('APP_SECRET')

    db.init_app(app)
    jwt.init_app(app)

    from .routes.auth import auth_bp
    from .routes.user import user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)

    with app.app_context():
        db.create_all()

    return app