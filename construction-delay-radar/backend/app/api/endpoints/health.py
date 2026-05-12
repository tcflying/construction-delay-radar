from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Construction Delay Radar API",
        "version": "0.1.0",
    }
