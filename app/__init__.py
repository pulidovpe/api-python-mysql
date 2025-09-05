from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from config import get_config
import time
import os

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from prometheus_client import generate_latest

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    load_dotenv()

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(get_config())

    if app.config.get("TESTING"):
        app.config["JWT_SECRET_KEY"] = "test_secret"

    db.init_app(app)
    jwt.init_app(app)

    # --------- 🔹 IMPORTAR MODELOS AQUÍ ---------
    from app.models.user import User

    # --------- CONFIGURACIÓN OTEL ---------
    resource = Resource(attributes={SERVICE_NAME: "api-python-mysql"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://collector:4317')
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[PrometheusMetricReader()]))
    meter = metrics.get_meter(__name__)
    app.request_counter = meter.create_counter("http.requests.total", description="Número total de requests")
    FlaskInstrumentor().instrument_app(app)

    @app.route('/metrics')
    def metrics_route():
        return generate_latest(), 200, {'Content-Type': 'text/plain; version=0.0.4'}

    # --------- 🔹 CREAR TABLAS ---------
    def wait_for_db_and_create_tables():
        max_retries = 10
        retry_delay = 5
        for i in range(max_retries):
            try:
                with app.app_context():
                    print("Intentando conectar a la DB y crear tablas...")
                    SQLAlchemyInstrumentor().instrument(engine=db.engine)
                    db.create_all()
                    print("Tablas creadas correctamente.")
                    return
            except Exception as e:
                print(f"Error creando tablas: {e}. Reintentando en {retry_delay} segundos...")
                time.sleep(retry_delay)
        print("¡Error fatal! No se pudo conectar a la base de datos.")
        exit(1)

    if not app.config.get("PRODUCTION"):
        wait_for_db_and_create_tables()

    # --------- 🔹 REGISTRAR RUTAS DESPUÉS ---------
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)

    return app
