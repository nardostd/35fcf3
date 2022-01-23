from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ProspectFileStatus(str, Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    done = "done"


class ProspectFile(BaseModel):
    id: int
    file_name: str
    file_size: int
    sha512_digest: str
    file_path: str
    email_index: int
    first_name_index: Optional[int]
    last_name_index: Optional[int]
    has_headers: Optional[bool]
    force: Optional[bool]
    rows_total: int
    rows_done: int
    uploaded_at: datetime
    user_id: int
    status: ProspectFileStatus

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
    has_headers: bool
    force: bool
    uploaded_at: datetime
    status: ProspectFileStatus
