import csv
from pydantic import ValidationError
from api.core.config import settings
from api.schemas.prospects import ProspectCreate
from api.core.logger import log


def process_csv_file(file_params: dict) -> dict:
    """
    Process CSV file with given parameters

    This utility method expects the following file parameters:
        "file_path" - required
        "email_index" - required
        "first_name_index" - optional
        "last_name_index" - optional
        "has_headers" - optional
    """

    # a collection to hold the discovered prospects
    prospects: set = set()

    # count the number of lines in the csv file
    total_number_of_lines: int = 0

    # read csv file from disk
    with open(
        file_params["file_path"], newline="", buffering=settings.BUFFER_SIZE
    ) as csvfile:

        rows = csv.reader(csvfile, delimiter=",", quotechar='"')

        # if csv file has a header skip it
        if file_params["has_headers"] == True:
            next(rows, None)

        for row in rows:
            # limit the number of rows to configured value of API
            if total_number_of_lines > settings.MAX_NUMBER_OF_ROWS:
                break

            # one more row is read
            total_number_of_lines += 1

            # skip invalid/malformed rows
            if is_valid_row(row, file_params) == False:
                continue

            try:
                # get email
                email = row[file_params["email_index"] - 1]

                # get first name or default to empty string
                if not file_params["first_name_index"]:
                    first_name = ""
                else:
                    first_name = row[file_params["first_name_index"] - 1]

                # get last name or default to empty string
                if not file_params["last_name_index"]:
                    last_name = ""
                else:
                    last_name = row[file_params["last_name_index"] - 1]

                # create the prospect object and add to collection
                prospects.add(
                    ProspectCreate(
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                    )
                )

            except ValidationError as e:
                log.error(e.errors()[0]["msg"])

    # compose appropriate result and return
    return {
        "prospects": prospects,
        "lines_read": total_number_of_lines,
    }


# Invalid if the number of columns discovered in the row
# is less than any of the indices provided in the request.
def is_valid_row(row: list, file_params: dict) -> bool:
    """Validate a row in a CSV file. Mainly check if indices are not out of bound."""
    try:
        if (
            file_params["email_index"] < 1
            or file_params["email_index"] > len(row)
            or (
                file_params["first_name_index"] is not None
                and file_params["first_name_index"] > len(row)
            )
            or (
                file_params["last_name_index"] is not None
                and file_params["last_name_index"] > len(row)
            )
        ):
            raise ValueError("index out of bound.")
        return True

    except (ValueError):
        return False
