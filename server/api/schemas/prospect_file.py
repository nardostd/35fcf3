from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ProspectFile(BaseModel):
    id: int
    file_name: str
    file_size: int
    sha512_digest: str
    file_path: str
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


class ProspectFileCreate(BaseModel):
    file_name: str
    file_size: int
    sha512_digest: str
    file_path: str
    email_index: int
    first_name_index: Optional[int]
    last_name_index: Optional[int]
    has_header: bool
    uploaded_at: datetime
