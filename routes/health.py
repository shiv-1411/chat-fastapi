from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/health")
def health_check():
    print("Health check endpoint called")  # Debug log
    return {"status": "ok"} 