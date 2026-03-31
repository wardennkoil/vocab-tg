from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_user_service, get_word_service
from app.schemas.word import (
    AddWordRequest,
    PaginatedUserWords,
    UserWordResponse,
    WordCard,
    WordSuggestion,
)
from app.services.user_service import UserService
from app.services.word_service import WordService

router = APIRouter(tags=["words"])


@router.get("/words/search", response_model=list[WordSuggestion])
async def search_words(
    q: str,
    word_service: WordService = Depends(get_word_service),
):
    suggestions = await word_service.suggest_words(q)
    return [WordSuggestion(word=s.word, score=s.score) for s in suggestions]


@router.get("/words/{word}", response_model=WordCard)
async def get_word(
    word: str,
    word_service: WordService = Depends(get_word_service),
):
    return await word_service.get_word_card(word)


@router.post("/users/{telegram_id}/words", response_model=UserWordResponse)
async def add_word(
    telegram_id: int,
    data: AddWordRequest,
    word_service: WordService = Depends(get_word_service),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_word = await word_service.add_custom_word(user.id, data.word)
    return user_word


@router.get("/users/{telegram_id}/words", response_model=PaginatedUserWords)
async def get_user_words(
    telegram_id: int,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
    word_service: WordService = Depends(get_word_service),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    items, total = await word_service.get_user_words(
        user.id, status=status, page=page, per_page=per_page
    )
    return PaginatedUserWords(items=items, total=total, page=page, per_page=per_page)


@router.delete("/users/{telegram_id}/words/{user_word_id}")
async def delete_user_word(
    telegram_id: int,
    user_word_id: int,
    word_service: WordService = Depends(get_word_service),
    user_service: UserService = Depends(get_user_service),
):
    user = await user_service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    deleted = await word_service.remove_user_word(user.id, user_word_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Word not found in user's list")
    return {"status": "deleted"}
