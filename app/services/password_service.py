from __future__ import annotations

import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.config import Config
from app.repositories.password_reset_repository import PasswordResetRepository
from app.services.user_service import UserService
from app.utils.exceptions import NotFoundError, ValidationError


class PasswordService:
    def __init__(self, repo: Optional[PasswordResetRepository] = None, user_service: Optional[UserService] = None) -> None:
        self._repo = repo or PasswordResetRepository()
        self._users = user_service or UserService()

    def list_requests(self, user_id: Optional[int] = None):
        if user_id:
            return self._repo.get_by_user(user_id)
        return self._repo.get_all()

    def create_request(self, user_id: int, email: str) -> int:
        if not user_id or not email:
            raise ValidationError(message="Missing required fields")
        token = secrets.token_urlsafe(32)
        request_id = self._repo.create(user_id, email, token)
        link = f"{Config.RESET_PASSWORD_URL_BASE}/{request_id}/{user_id}/{token}"
        self._send_email(email, link)
        return request_id

    def reset_password(self, request_id: int, user_id: int, new_password: str) -> None:
        if not request_id or not user_id or not new_password:
            raise ValidationError(message="Missing required fields")
        if not self.validate_token(request_id):
            raise ValidationError(message="Token invalid or expired")
        self._users.update_password(user_id, new_password)
        self._repo.mark_used(request_id)

    def validate_token(self, request_id: int) -> bool:
        token = self._repo.get_token_info(request_id)
        if not token:
            return False
        if token.get("utilizado") == "S":
            return False
        expires_at = self._parse_datetime(token.get("ti_validade"))
        if not expires_at:
            created_at = self._parse_datetime(token.get("timestamp"))
            if created_at:
                expires_at = created_at + timedelta(hours=24)
        if expires_at and datetime.now() > expires_at:
            return False
        return True

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            return None

    @staticmethod
    def _send_email(destinatario: str, link: str) -> None:
        if not Config.EMAIL_USER or not Config.EMAIL_PASSWORD:
            raise ValidationError(message="Email credentials not configured")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Recuperacao de senha - MenTech"
        msg["From"] = Config.EMAIL_USER
        msg["To"] = destinatario

        corpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #4EA2A9; padding: 40px; margin: 0;">
            <div style="background: #F5F5F5; border-radius: 15px; padding: 30px; max-width: 600px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;">
            <h2 style="color: #4EA2A9; margin-bottom: 20px;">Recuperacao de senha</h2>
            <p style="color: #333; font-size: 16px; line-height: 1.5;">
                Voce solicitou a redefinicao de senha. Clique no botao abaixo para criar uma nova:
            </p>
            <a href="{link}" style="display: inline-block; background: #B39DDB; color: white; text-decoration: none; padding: 12px 25px; border-radius: 8px; font-weight: bold; font-size: 16px; margin: 20px 0;">
                Renovar senha
            </a>
            <p style="color: #999; font-size: 11px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
                Este link expira em 24 horas por motivos de seguranca.
            </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(corpo_html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.sendmail(Config.EMAIL_USER, destinatario, msg.as_string())
