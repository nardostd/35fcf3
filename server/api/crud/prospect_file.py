import hashlib
from traceback import print_stack
import uuid
import logging
from fastapi import logger
from sqlalchemy import update
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

        # save file to disk... this is a hack (i.e. not a CRUD operation)!

        # check if the same exact file exists in disk (using sha512 digest)
        existing_file_path = (
            db.query(ProspectFile.file_path)
            .filter_by(sha512_digest=hashlib.sha512(contents).hexdigest())
            .first()
        )

        # if file already exists, it must have been processed previously
        # return null so that caller knows the file cannot be processed.
        if existing_file_path is not None:
            return None

        # generate unique filename and save file to disk
        file_path = f"{settings.CSV_FILES_PATH}/{uuid.uuid4().hex}.csv"
        # TODO loads everything into memory - improve!
        with open(file_path, "wb+") as csv_file:
            csv_file.write(contents)
        log.info(f"New file created: {file_path}")

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
        db.query(ProspectFile).filter(ProspectFile.id == data["id"]).update({**data})
        db.commit()

    @classmethod
    def get_prospect_file_by_id(cls, db: Session, file_id: int) -> ProspectFile:
        return db.query(ProspectFile).filter_by(id=file_id).first()
