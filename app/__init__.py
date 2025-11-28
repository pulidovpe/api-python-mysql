from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from config import get_config
import sqlalchemy
from sqlalchemy import text as sql_text
import logging

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
    from .routes.health import health_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(health_bp)

    # Crear tablas en entornos no productivos
    if app.config.get("TESTING") or app.config.get("DEBUG"):
        with app.app_context():
            try:
                db.create_all()
            except Exception as e:
                # Evitar que la aplicación se caiga si la base de datos no está disponible
                # (por ejemplo en pruebas locales con DB en otro contenedor/host).
                import logging
                logging.warning("No se pudieron crear las tablas al iniciar: %s", e)

    # Registrar manejador de errores para problemas de base de datos
    def _db_unavailable_handler(error):
        logging.exception("Database error intercepted: %s", error)
        payload = {
            "message": "database_unavailable",
            "detail": "La base de datos no está disponible",
            "error": str(error),
        }
        return jsonify(payload), 503

    # Manejar errores comunes de SQLAlchemy para que la app no caiga
    app.register_error_handler(sqlalchemy.exc.OperationalError, _db_unavailable_handler)
    app.register_error_handler(sqlalchemy.exc.DatabaseError, _db_unavailable_handler)

    # Comprobar la conexión a la BD antes de ejecutar vistas que la requieran.
    # Excluimos la ruta /health y activos estáticos para no interferir con los cheks.
    @app.before_request
    def _check_db_before_request():
        # Permitir omitir las comprobaciones cuando se lanza la imagen solo para validar
        # el contenedor (por ejemplo en AWS Fargate) estableciendo `SKIP_DB_CHECKS=true`.
        skip_checks = str(app.config.get('SKIP_DB_CHECKS', False)).lower() in ('1', 'true', 'yes')
        if skip_checks:
            return None
        # No chequear en health endpoint ni para opciones
        if request.path.startswith('/health') or request.method == 'OPTIONS' or request.path.startswith('/static'):
            return None

        try:
            # Hacemos una comprobación breve y liviana
            with db.engine.connect() as conn:
                conn.execute(sql_text("SELECT 1"))
        except Exception as exc:
            logging.exception("DB connectivity check failed: %s", exc)
            payload = {
                "message": "database_unavailable",
                "detail": "La aplicación no puede conectarse a la base de datos. Inténtelo más tarde.",
                "error": str(exc),
            }
            return jsonify(payload), 503

    @app.route('/')
    def index():
        return {'response': 'Flask RESTful API'}, 200

    return app
