from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_user_service
from app.schemas.user import UserRegister, UserResponse, UserSettingsUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse)
async def register_user(
    data: UserRegister,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_or_create_user(
        telegram_id=data.telegram_id,
        username=data.username,
        first_name=data.first_name,
        language_code=data.language_code,
    )
    return user


@router.get("/{telegram_id}", response_model=UserResponse)
async def get_user(
    telegram_id: int,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{telegram_id}/settings", response_model=UserResponse)
async def update_settings(
    telegram_id: int,
    data: UserSettingsUpdate,
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_service.update_settings(user, data)
