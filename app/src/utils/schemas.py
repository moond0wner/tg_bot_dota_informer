"""Validation schemas"""

from pydantic import BaseModel, field_validator
from pydantic_core import ValidationError


class AccountSchema(BaseModel):
    account_id: int

    @field_validator("account_id")
    def account_id_must_be_valid(cls, value):
        if not isinstance(value, int):
            raise ValueError("ID аккаунта должен содержать только цифры.")
        if value <= 0:
            raise ValidationError("ID аккаунта должен быть больше нуля.")
        return value


class MatchSchema(BaseModel):
    match_id: int

    @field_validator("match_id")
    def match_id_must_be_valid(cls, value):
        if not isinstance(value, int):
            raise ValueError("ID матча должен содержать только цифры.")
        if value <= 0:
            raise ValidationError("ID матча должен быть больше нуля.")
        return value
