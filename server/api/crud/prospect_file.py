import hashlib
import uuid
import logging
from fastapi import logger
from sqlalchemy.orm.session import Session

from api.models import ProspectFile, prospect_file
from api.core.config import settings
from api import schemas

logging.basicConfig(level=logging.INFO)
log = logger.logger


class ProspectFileCrud:
    @classmethod
    def create_prospect_file(
        cls,
        db: Session,
        user_id: int,
        meta_data: schemas.ProspectFileCreate,
        contents: bytes,
    ) -> ProspectFile:
        """Save uploaded file to disk and its meta data to database"""

        # check if the same exact file exists in disk (using sha512 digest)
        existing_file = (
            db.query(ProspectFile)
            .filter_by(sha512_digest=hashlib.sha512(contents).hexdigest())
            .first()
        )

        # if file does not exist, generate file_path and save it to disk
        if existing_file is None:
            # generate unique filename and save file to disk
            file_path = f"{settings.CSV_FILES_PATH}/{uuid.uuid4().hex}.csv"
            # TODO loads everything into memory - improve!
            with open(file_path, "wb+") as csv_file:
                csv_file.write(contents)
        else:
            # if file already exists, check if the incoming index parameters are different
            existing_email_index = existing_file.email_index
            existing_first_name_index = existing_file.first_name_index
            existing_last_name_index = existing_file.last_name_index
            # if index parameters are exactly the same, do not process request
            if (
                existing_email_index == meta_data["email_index"]
                and existing_first_name_index == meta_data["first_name_index"]
                and existing_last_name_index == meta_data["last_name_index"]
            ):
                return None

            # if at least one of the index parameters is different, process request
            file_path = existing_file.file_path

        # create entity and persist to database
        prospect_file = ProspectFile(
            **meta_data,
            rows_total=0,
            rows_done=0,
            user_id=user_id,
            file_path=file_path,
        )
        db.add(prospect_file)
        db.commit()
        db.refresh(prospect_file)

        return prospect_file

    @classmethod
    def update_prospect_file(cls, db: Session, data: ProspectFile) -> ProspectFile:
        """Update ProspectFile"""
        prospect_file = ProspectFile(**data)
        db.query(ProspectFile).filter(ProspectFile.id == data["id"]).update({**data})
        db.commit()
        return prospect_file

    @classmethod
    def get_prospect_file_by_id(cls, db: Session, file_id: int) -> ProspectFile:
        """Get the ProspectFile with given id"""
        return db.query(ProspectFile).filter_by(id=file_id).first()

    @classmethod
    def get_prospect_file_by_request_id(
        cls, db: Session, request_id: str
    ) -> ProspectFile:
        """Get the ProspectFile with given request id"""
        return db.query(ProspectFile).filter_by(request_id=request_id).first()
