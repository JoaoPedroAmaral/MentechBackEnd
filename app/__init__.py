from __future__ import annotations

from flask import Flask, request, g
from flask_cors import CORS

from app.config import Config
from app.routes.user_routes import user_bp
from app.routes.auth_routes import auth_bp
from app.routes.password_routes import password_bp
from app.routes.disorder_routes import disorder_bp
from app.routes.patient_routes import patient_bp
from app.routes.patient_anamnese_routes import anamnese_bp
from app.routes.patient_disorder_routes import patient_disorder_bp
from app.routes.patient_medication_routes import patient_medication_bp
from app.routes.appointment_routes import appointment_bp
from app.routes.behavior_routes import behavior_bp
from app.routes.medication_routes import medication_bp
from app.routes.goal_routes import goal_bp
from app.routes.activity_routes import activity_bp
from app.routes.log_routes import log_bp
from app.routes.pathology_routes import pathology_bp
from app.routes.responsible_routes import responsible_bp
from app.routes.medical_record_routes import medical_record_bp
from app.routes.gender_routes import gender_v1_bp
from app.routes.address_routes import address_bp
from app.utils.exceptions import AppError
from app.utils.response import error


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    @app.before_request
    def capture_user_context():
        user_id = request.headers.get("x-usuario-id")
        if user_id and user_id.isdigit():
            g.user_id = int(user_id)
        else:
            g.user_id = None

    @app.errorhandler(AppError)
    def handle_app_error(e: AppError):
        return error(e.message, e.status_code, e.to_dict())

    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(password_bp)
    app.register_blueprint(disorder_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(anamnese_bp)
    app.register_blueprint(patient_disorder_bp)
    app.register_blueprint(patient_medication_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(behavior_bp)
    app.register_blueprint(medication_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(pathology_bp)
    app.register_blueprint(responsible_bp)
    app.register_blueprint(medical_record_bp)
    app.register_blueprint(gender_v1_bp)
    app.register_blueprint(address_bp)

    return app
