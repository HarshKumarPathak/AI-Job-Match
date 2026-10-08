from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Candidate, User
from app.services.auth import create_access_token, hash_password, verify_password


def test_password_hash_round_trip():
    hashed = hash_password("StrongPass123!")
    assert hashed != "StrongPass123!"
    assert verify_password("StrongPass123!", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_contains_user_id():
    token = create_access_token(42)
    assert isinstance(token, str)
    assert len(token) > 20


def test_user_candidate_relationship_is_unique():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        candidate = Candidate(email="test@example.com")
        db.add(candidate)
        db.flush()
        db.add(User(email="test@example.com", password_hash="hash", candidate_id=candidate.id))
        db.commit()
        assert db.scalar(User.email.property.columns[0].type.python_type == str)
