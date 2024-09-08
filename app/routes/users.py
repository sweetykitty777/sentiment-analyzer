from fastapi import APIRouter, Depends

from app.dependencies import get_user
from app.models.user import User

router = APIRouter()


@router.get("/users/me", summary="Get information about the current user")
def get_me(user: User = Depends(get_user)) -> User:
    return user
