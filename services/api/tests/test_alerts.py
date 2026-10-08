from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.alerts import create_alert, get_alert, update_alert
from app.db import Base
from app.models import AlertNotification, Candidate, Job, User
from app.schemas.alert import JobAlertCreate, JobAlertUpdate
from app.services.alert_service import mark_new_notifications
from app.services.recommendation_engine import RankedRecommendation


def test_alert_create_get_and_update() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(name="Alert User", email="alert@example.com")
        db.add(candidate)
        db.commit()

        user = User(
            email="alert@example.com",
            password_hash="test-hash",
            candidate_id=candidate.id,
        )
        db.add(user)
        db.commit()

        alert = create_alert(
            JobAlertCreate(candidate_id=candidate.id, minimum_score=80),
            db,
            user,
        )
        assert alert.minimum_score == 80
        assert alert.enabled is True

        loaded = get_alert(candidate.id, db, user)
        assert loaded is not None
        assert loaded.id == alert.id

        updated = update_alert(
            alert.id,
            JobAlertUpdate(minimum_score=90, enabled=False),
            db,
            user,
        )
        assert updated.minimum_score == 90
        assert updated.enabled is False


def test_alert_matches_are_deduplicated_by_alert_and_job() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(name="Alert User", email="alert2@example.com")
        job = Job(title="Python Intern", company="Example")
        db.add_all([candidate, job])
        db.commit()

        user = User(
            email="alert2@example.com",
            password_hash="test-hash",
            candidate_id=candidate.id,
        )
        db.add(user)
        db.commit()

        alert = create_alert(
            JobAlertCreate(candidate_id=candidate.id, minimum_score=70),
            db,
            user,
        )
        recommendation = RankedRecommendation(
            job=job,
            score=85,
            matched_skills=("python",),
            missing_skills=(),
            reasons=("1 required skills matched",),
        )

        first = mark_new_notifications(db, alert, [recommendation])
        assert [item.job.id for item in first] == [job.id]

        db.add(AlertNotification(alert_id=alert.id, job_id=job.id, score=85))
        db.commit()

        second = mark_new_notifications(db, alert, [recommendation])
        assert second == []
