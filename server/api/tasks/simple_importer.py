import logging
import logging
from sqlalchemy.orm.session import Session
from fastapi import Depends, logger
from api.dependencies.db import get_db
from api.schemas.prospects_file import ProspectsFile, ProspectsFileCreate
from api.crud import ProspectsFileCrud

logging.basicConfig(level = logging.INFO)
log = logger.logger

def process_file(file_id: int, force: bool):
    """Persist prospects file and trigger background task"""
    log.info(file_id)