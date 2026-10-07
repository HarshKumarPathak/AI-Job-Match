from fastapi import APIRouter

from app.api.candidates import router as candidates_router

router = APIRouter()
router.include_router(candidates_router)
