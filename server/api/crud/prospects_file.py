from sqlalchemy.orm.session import Session

from api.models import ProspectsFile
from api import schemas

class ProspectsFileCrud:
    @classmethod
    def create_prospects_file(
        cls,
        db: Session,
        user_id: int,
        data: schemas.ProspectsFileCreate
    ) -> ProspectsFile:
        """Persist uploaded file"""
        prospects_file = ProspectsFile(
            **data,
            rows_total = 0,
            rows_done = 0,
            user_id=user_id,
        )
        db.add(prospects_file)
        db.commit()
        db.refresh(prospects_file)
        return prospects_file
