from fastapi import APIRouter, HTTPException, status

from app.core.security import create_access_token
from app.schemas.auth import TokenRequest, TokenResponse


router = APIRouter()


@router.post("/token", response_model=TokenResponse)
async def token(payload: TokenRequest) -> TokenResponse:
    if not payload.username or not payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username and password required")
    # Replace with a User repository before multi-user deployment.
    return TokenResponse(access_token=create_access_token(payload.username, "admin"))
