from typing import Set
from sqlalchemy.orm.session import Session
from api.schemas.prospects import Prospect
from api.crud.prospect import ProspectCrud


def persist(db: Session, prospects: set, params: dict) -> Set[Prospect]:
    """
    Persists a collection of Prospects.
    Updates if Prospect already exists and the 'force' flag is set.
    """

    persisted_prospects: Set[Prospect] = set()

    # iterate over the discovered prospects and persist
    for prospect in prospects:

        data = {
            "email": prospect.email,
            "first_name": prospect.first_name,
            "last_name": prospect.last_name,
        }

        # check if prospect with same email exists
        existing_prospect = ProspectCrud.get_prospect_by_email(db, prospect.email)

        # if there is a prospect with same email and the force flag is true
        if existing_prospect is not None:
            if params["force"] == True:
                persisted_prospects.add(
                    ProspectCrud.update_prospect(
                        db,
                        params["user_id"],
                        data,
                    )
                )
        else:
            persisted_prospects.add(
                ProspectCrud.create_prospect(
                    db,
                    params["user_id"],
                    data,
                )
            )

    return persisted_prospects
