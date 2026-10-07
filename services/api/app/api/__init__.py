from fastapi import APIRouter

from app.api.candidates import router as candidates_router
from app.api.resumes import router as resumes_router

router = APIRouter()
router.include_router(candidates_router)
router.include_router(resumes_router)
