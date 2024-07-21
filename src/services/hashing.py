import hashlib

from passlib.context import CryptContext

from src.settings import project_settings

pwd_context: CryptContext = CryptContext(
    schemes=[
        "bcrypt",
    ],
    deprecated="auto",
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_signature(data: dict) -> bool:
    received_signature = data.get("signature", False)
    return received_signature


def _generate_signature(data: dict) -> str:
    data.pop("signature", None)
    concatenated_values = "".join(str(data[key]) for key in sorted(data.keys()))
    concatenated_values += project_settings.SECRET_KEY
    signature = hashlib.sha256(concatenated_values.encode("utf-8")).hexdigest()
    return signature
