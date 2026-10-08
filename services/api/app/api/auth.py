from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Candidate, User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    candidate = db.scalar(select(Candidate).where(Candidate.email == email))
    if candidate is None:
        candidate = Candidate(name=payload.name, email=email)
        db.add(candidate)
        db.flush()
    else:
        candidate.name = payload.name

    user = User(email=email, password_hash=hash_password(payload.password), candidate_id=candidate.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(
        access_token=create_access_token(user.id),
        candidate_id=candidate.id,
        name=candidate.name,
        email=email,
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    candidate = db.get(Candidate, user.candidate_id)
    if candidate is None:
        raise HTTPException(status_code=500, detail="Account profile is missing")

    return AuthResponse(
        access_token=create_access_token(user.id),
        candidate_id=candidate.id,
        name=candidate.name,
        email=user.email,
    )


@router.get("/me", response_model=AuthResponse)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> AuthResponse:
    candidate = db.get(Candidate, user.candidate_id)
    if candidate is None:
        raise HTTPException(status_code=500, detail="Account profile is missing")
    return AuthResponse(
        access_token="",
        candidate_id=candidate.id,
        name=candidate.name,
        email=user.email,
    )
