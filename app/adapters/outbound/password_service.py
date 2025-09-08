import bcrypt

from app.core.ports.auth import PasswordServicePort


class BcryptPasswordService(PasswordServicePort):
    """Implementação do serviço de hashing de senhas com bcrypt."""

    def hash_password(self, password: str) -> str:
        """Gera hash da senha."""
        # Gera salt e hash da senha
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha corresponde ao hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
