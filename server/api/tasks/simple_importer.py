import csv
import logging
from array import array
from typing import Set
from sqlalchemy.orm.session import Session
from fastapi import Depends, logger
from pydantic import EmailStr, EmailError, ValidationError
from api.dependencies.db import get_db
from api.schemas.prospect_file import ProspectFile, ProspectFileCreate
from api.crud import ProspectFileCrud
from api.schemas.prospects import Prospect

logging.basicConfig(level=logging.INFO)
log = logger.logger


def process_file(db, file_id: int) -> Set[Prospect]:
    """Process prospect file identified by file_id"""

    # get file meta data from database
    prospect_file = ProspectFileCrud.get_prospect_file_by_id(db, file_id)

    # TODO actual csv file processing
    # read csv file from disk
    with open(prospect_file.file_path, newline="") as csvfile:
        prospects = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in prospects:
            # make assumptions about first name and last name indices if not provided
            if prospect_file.first_name_index < 1 or prospect_file.last_name_index < 1:
                name_index = get_name_indices(row, prospect_file)
                prospect_file.first_name_index = name_index[0]
                prospect_file.last_name_index = name_index[1]

            # validate row
            if is_valid_prospect(row, prospect_file):
                discovered_prospects: set = set()
                discovered_prospects.add(
                    Prospect(
                        email=row[prospect_file.email_index - 1],
                        first_name=row[prospect_file.first_name_index - 1],
                        last_name=row[prospect_file.last_name_index - 1],
                    )
                )
                return discovered_prospects
            return set()


# TODO do this correctly!
def get_name_indices(row: list, prospect_file: ProspectFile) -> array:
    cols = len(row)
    email_index = prospect_file.email_index
    first_name_index = prospect_file.first_name_index
    last_name_index = prospect_file.last_name_index
    # TODO
    return array(email_index, email_index)


# validate a row in a CSV file
# TODO add more validators
def is_valid_prospect(row: list, prospect_file: ProspectFile) -> bool:
    email_index = prospect_file.email_index
    first_name_index = prospect_file.first_name_index
    last_name_index = prospect_file.last_name_index
    cols = len(row)
    try:
        # index out of bound errors
        if (
            email_index < 1
            or email_index > cols
            or first_name_index > cols
            or last_name_index > cols
        ):
            raise ValueError("index out of bound.")

        # bad email
        EmailStr.validate(row[email_index - 1])

        # both first and last names are empty
        if len(row[first_name_index - 1]) == 0 and len(row[last_name_index - 1]) == 0:
            raise ValueError("at least one name is required.")

        return True
    except (ValidationError, EmailError, ValueError):
        return False
