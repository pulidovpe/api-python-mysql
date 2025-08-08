from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from config import get_config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    load_dotenv()

    # Cargar configuración según entorno
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(get_config())

    # 🔹 Forzar clave JWT en entorno de testing
    if app.config.get("TESTING"):
        app.config["JWT_SECRET_KEY"] = "test_secret"

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)

    # Registrar blueprints
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)

    # Crear tablas en entornos no productivos
    if app.config.get("TESTING") or app.config.get("DEBUG"):
        with app.app_context():
            db.create_all()

    @app.route('/')
    def index():
        return {'response': 'Flask RESTful API'}, 200

    return app
