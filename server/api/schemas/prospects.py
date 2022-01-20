from datetime import datetime
from typing import List

from pydantic import BaseModel
from pydantic.networks import EmailStr


class Prospect(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# made hashable by @nardos
class ProspectCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

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
