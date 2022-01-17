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
    file_name = Column(String, index=True, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    sha512_digest = Column(String, index=True, unique=True)
    email_index = Column(Integer, nullable=False)
    first_name_index = Column(Integer, nullable=False)
    last_name_index = Column(Integer, nullable=False)
    has_header = Column(Boolean, nullable=False)
    rows_total = Column(Integer, nullable=False)
    rows_done = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(BigInteger, ForeignKey("users.id"))

    uploaded_by = relationship(
        "User", back_populates="prospect_files", foreign_keys=[user_id]
    )

    def __repr__(self):
        return f"{self.id} | {self.sha512_digest}"