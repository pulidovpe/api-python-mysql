from flask import Blueprint, jsonify
from sqlalchemy import text
from app import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health():
    """Health endpoint for load balancers / orchestrators.

    Returns JSON with service status and a lightweight DB check.
    The DB check uses a direct engine connection and executes a simple
    `SELECT 1` to avoid session/transaction side-effects.
    If the DB is unreachable the endpoint returns 503 so an external
    health-checker (like an AWS ALB target group) can detect degraded state.
    """
    payload = {"service": "ok"}

    try:
        # Use a short engine connection to perform a trivial read
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        payload["database"] = "ok"
        status_code = 200
    except Exception as exc:
        payload["database"] = "unreachable"
        payload["error"] = str(exc)
        status_code = 503

    return jsonify(payload), status_code
