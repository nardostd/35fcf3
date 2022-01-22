from datetime import datetime
import imp
from typing import List
from pydantic import ValidationError, validator

from pydantic import BaseModel, EmailStr


class Prospect(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    @validator("email")
    def email_must_be_valid(cls, v):
        """The email field must be a valid email string"""
        EmailStr.validate(v)
        return v

    class Config:
        orm_mode = True

    def __eq__(self, other):
        return other is Prospect and self.email == other.email

    def __hash__(self):
        return hash((self.email, self.first_name, self.last_name))


# made hashable by @nardos
class ProspectCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

    @validator("email")
    def email_must_be_valid(cls, v):
        """The email field must be a valid email string"""
        EmailStr.validate(v)
        return v

    def __eq__(self, other):
        return (
            other is ProspectCreate
            and self.email == other.email
            and self.first_name == other.first_name
            and self.last_name == other.last_name
        )

    def __hash__(self):
        return hash((self.email, self.first_name, self.last_name))


class ProspectResponse(BaseModel):
    """One page of prospects"""

    prospects: List[Prospect]
    size: int
    total: int
