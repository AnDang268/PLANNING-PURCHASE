
from fastapi import APIRouter
router = APIRouter()

@router.get("/unique_ping")
def unique_ping():
    return {"message": "I AM LIVE AND UPDATED"}
