from enum import unique
from xmlrpc.client import Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import BigInteger, Integer, String, DateTime, Boolean
from api.database import Base


class ProspectFile(Base):
    """Prospect Files Table"""

    __tablename__ = "prospect_files"

    id = Column(BigInteger, primary_key=True, autoincrement=True, unique=True)
    file_name = Column(String, index=False, nullable=False, unique=False)
    file_size = Column(BigInteger, nullable=False)
    sha512_digest = Column(String, index=False, unique=False, nullable=False)
    file_path = Column(String, nullable=False)
    email_index = Column(Integer, nullable=False)
    first_name_index = Column(Integer, nullable=True)
    last_name_index = Column(Integer, nullable=True)
    has_headers = Column(Boolean, nullable=True)
    force = Column(Boolean, nullable=True)
    rows_total = Column(Integer, nullable=False)
    rows_done = Column(Integer, nullable=False)
    uploaded_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    uploaded_by = relationship(
        "User", back_populates="prospect_files", foreign_keys=[user_id]
    )

    status = Column(String, nullable=False)
    request_id = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"{self.id} | {self.sha512_digest}"
