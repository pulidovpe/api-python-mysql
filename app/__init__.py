# app/__init__.py

import os
import time
from flask import Flask, request
from werkzeug.routing import Rule
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricsExporter
from prometheus_client import start_http_server

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(get_config())

    db.init_app(app)
    jwt.init_app(app)

    # ==== Tracing
    resource = Resource(attributes={SERVICE_NAME: "api-python-mysql"})
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://alloy:4317")
    span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))

    # ==== Metrics (Prometheus)
    exporter = PrometheusMetricsExporter()
    reader = PeriodicExportingMetricReader(exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)
    meter = metrics.get_meter(__name__)

    # Contador y histograma con convención Prom
    counter = meter.create_counter("http_requests_total", description="Total HTTP requests")
    histogram = meter.create_histogram("http_request_duration_seconds", unit="s", description="HTTP request duration")

    # Iniciar endpoint /metrics
    start_http_server(int(os.getenv("APP_METRICS_PORT", 9464)))

    def get_route():
        rule = request.url_rule
        return rule.rule if rule and isinstance(rule, Rule) else request.path or "unknown"

    @app.before_request
    def start_timer():
        request._start_time = time.perf_counter()

    @app.after_request
    def record_metrics(response):
        elapsed = time.perf_counter() - getattr(request, "_start_time", time.perf_counter())
        labels = {
            "method": request.method,
            "route": get_route(),
            "status_code": str(response.status_code)
        }
        counter.add(1, labels)
        histogram.record(elapsed, labels)
        return response

    # Registrar blueprints, rutas, etc.
    from app.models import *
    db.create_all(app=app)

    # opcional: instrumentar Flask app en traces
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    FlaskInstrumentor().instrument_app(app)

    return app
