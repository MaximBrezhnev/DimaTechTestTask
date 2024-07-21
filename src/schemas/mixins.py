import re
from typing import ClassVar
from typing import Optional

from pydantic import field_validator
from pydantic import model_validator


class UserValidationMixin:
    """Класс для проверки корректности переданных пользовательских данных"""

    FULL_NAME_LETTER_MATCH_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"^[а-яА-Яa-zA-Z\- ]+$"
    )
    MIN_FULL_NAME_LENGTH: ClassVar[int] = 1
    MAX_FULL_NAME_LENGTH: ClassVar[int] = 20

    MIN_PASSWORD_LENGTH: ClassVar[int] = 8
    PASSWORD_SPECIAL_SYMBOLS: ClassVar[str] = "!@#$%^&*()-_=+[{]};:'\",<.>/?\\|`~"

    @field_validator("full_name", check_fields=False)
    @classmethod
    def validate_full_name(cls, full_name: Optional[str]) -> Optional[str]:
        if full_name is not None:
            if (
                len(full_name) < cls.MIN_FULL_NAME_LENGTH
                or len(full_name) > cls.MAX_FULL_NAME_LENGTH
            ):
                raise ValueError("Incorrect full name length")

            if not cls.FULL_NAME_LETTER_MATCH_PATTERN.match(full_name):
                raise ValueError("The full name contains incorrect symbols")

            return full_name

    @classmethod
    def check_password_strength(cls, password: str) -> bool:
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return False

        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in cls.PASSWORD_SPECIAL_SYMBOLS for char in password)

        return has_upper and has_lower and has_digit and has_special

    @field_validator("password1", check_fields=False)
    @classmethod
    def validate_password(cls, password: str) -> str:
        if password is not None:
            if not cls.check_password_strength(password=password):
                raise ValueError("the password is weak")

            return password

    @model_validator(mode="before")
    @classmethod
    def check_password_match(cls, data: dict) -> dict:
        if data.get("password1", None) != data.get("password2", None):
            raise ValueError("the passwords do not match")

        return data
