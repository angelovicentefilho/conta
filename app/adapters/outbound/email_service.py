import logging

from app.core.ports.auth import EmailServicePort

logger = logging.getLogger(__name__)


class MockEmailService(EmailServicePort):
    """Implementação mock do serviço de e-mail para desenvolvimento."""

    async def send_password_reset_email(
        self, email: str, reset_token: str, user_name: str
    ) -> bool:
        """Envia e-mail de reset de senha (mock - apenas log)."""
        logger.info(f"[MOCK EMAIL] Password reset requested for {email}")
        logger.info(f"[MOCK EMAIL] Reset token: {reset_token}")
        logger.info(f"[MOCK EMAIL] User: {user_name}")
        logger.info(
            f"[MOCK EMAIL] Reset URL: "
            f"http://localhost:3000/reset-password?token={reset_token}"
        )

        # Em um ambiente real, aqui seria enviado o e-mail
        return True
