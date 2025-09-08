from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from app.config.settings import get_settings
from app.core.ports.auth import TokenServicePort


class JWTTokenService(TokenServicePort):
    """Implementação do serviço de tokens JWT."""

    def __init__(self):
        self._settings = get_settings()

    def create_access_token(self, user_id: str) -> str:
        """Cria um token de acesso JWT."""
        expiration = datetime.utcnow() + timedelta(
            seconds=self._settings.access_token_expire_seconds
        )

        payload = {
            "sub": user_id,
            "exp": expiration,
            "iat": datetime.utcnow(),
            "type": "access",
        }

        return jwt.encode(
            payload,
            self._settings.secret_key,
            algorithm=self._settings.algorithm,
        )

    def verify_token(self, token: str) -> Optional[str]:
        """Verifica e decodifica token JWT. Retorna user_id se válido."""
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.algorithm],
            )

            user_id = payload.get("sub")
            token_type = payload.get("type")

            if user_id and token_type == "access":
                return user_id

        except jwt.JWTError:
            pass

        return None

    def get_token_expiration_time(self) -> int:
        """Retorna o tempo de expiração do token em segundos."""
        return self._settings.access_token_expire_seconds
