from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("")
async def list_marketplace(_=Depends(get_current_user)):
    return []
