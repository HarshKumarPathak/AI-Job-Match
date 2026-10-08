from fastapi import APIRouter

from app.api.alerts import router as alerts_router
from app.api.auth import router as auth_router
from app.api.candidates import router as candidates_router
from app.api.jobs import router as jobs_router
from app.api.learning import router as learning_router
from app.api.matches import router as matches_router
from app.api.recommendations import router as recommendations_router
from app.api.resumes import router as resumes_router
from app.api.skill_gaps import router as skill_gaps_router
from app.api.tracking import router as tracking_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(candidates_router)
router.include_router(resumes_router)
router.include_router(jobs_router)
router.include_router(matches_router)
router.include_router(recommendations_router)
router.include_router(skill_gaps_router)
router.include_router(learning_router)
router.include_router(tracking_router)
router.include_router(alerts_router)
