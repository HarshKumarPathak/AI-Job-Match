from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.alerts import create_alert, get_alert, update_alert
from app.db import Base
from app.models import Candidate
from app.schemas.alert import JobAlertCreate, JobAlertUpdate


def test_alert_create_get_and_update() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(name="Alert User")
        db.add(candidate)
        db.commit()

        alert = create_alert(JobAlertCreate(candidate_id=candidate.id, minimum_score=80), db)
        assert alert.minimum_score == 80
        assert alert.enabled is True

        loaded = get_alert(candidate.id, db)
        assert loaded is not None
        assert loaded.id == alert.id

        updated = update_alert(
            alert.id,
            JobAlertUpdate(minimum_score=90, enabled=False),
            db,
        )
        assert updated.minimum_score == 90
        assert updated.enabled is False
