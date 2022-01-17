from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic.networks import EmailStr

class ProspectsFile(BaseModel):
    id: int
    file_name: str
    file_size: int
    sha512_digest: str
    email_index: int
    first_name_index: int
    last_name_index: int
    has_header: bool
    rows_total: int
    rows_done: int
    uploaded_at: datetime
    user_id: int

    class Config:
        orm_mode = True

class ProspectsFileCreate(BaseModel):
    file_name: str
    file_size: int
    sha512_digest: str
    email_index: int
    first_name_index: Optional[int]
    last_name_index: Optional[int]
    has_header: bool
    uploaded_at: datetime