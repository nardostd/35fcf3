from sqlalchemy.orm.session import Session

from api.models import ProspectFile
from api import schemas


class ProspectFileCrud:
    @classmethod
    def create_prospect_file(
        cls, db: Session, user_id: int, data: schemas.ProspectFileCreate
    ) -> ProspectFile:
        """Persist uploaded file"""
        prospects_file = ProspectFile(
            **data,
            rows_total=0,
            rows_done=0,
            user_id=user_id,
        )
        db.add(prospects_file)
        db.commit()
        db.refresh(prospects_file)
        return prospects_file
