from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.candidates import _to_read
from app.db import Base
from app.models import Candidate


def test_candidate_response_splits_stored_profile_lists() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        candidate = Candidate(
            name="Harsh",
            email="harsh@example.com",
            preferred_roles="AI Engineer\nBackend Developer",
            preferred_locations="Remote\nBengaluru",
            experience_years=1.0,
            education="B.Tech",
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

        result = _to_read(candidate)

        assert result.id == candidate.id
        assert result.preferred_roles == ["AI Engineer", "Backend Developer"]
        assert result.preferred_locations == ["Remote", "Bengaluru"]
        assert result.experience_years == 1.0
