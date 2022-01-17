import logging
import logging
from sqlalchemy.orm.session import Session
from fastapi import Depends, logger
from api.dependencies.db import get_db
from api.schemas.prospect_file import ProspectFile, ProspectFileCreate
from api.crud import ProspectFileCrud

logging.basicConfig(level = logging.INFO)
log = logger.logger

def process_file(file_id: int, force: bool):
    """Persist prospects file and trigger background task"""
    log.info(file_id)