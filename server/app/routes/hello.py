from fastapi import APIRouter

router = APIRouter(tags=["demo"])

@router.get("/", summary="Root says hello")
async def root():
    return {"message": "Hello from FastAPI!"}

@router.get("/ping", summary="Simple liveliness check")
async def ping():
    return {"pong": True}
