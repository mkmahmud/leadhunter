from fastapi import APIRouter

from app.api.v1 import auth, exports, leads, search


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(exports.router, prefix="/export", tags=["export"])
