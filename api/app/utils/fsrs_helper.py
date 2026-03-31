import json
from datetime import datetime, timedelta

from fsrs import Card, Rating, Scheduler

from app.config import settings

scheduler = Scheduler(
    desired_retention=settings.FSRS_DESIRED_RETENTION,
    learning_steps=(timedelta(minutes=1), timedelta(minutes=10)),
    relearning_steps=(timedelta(minutes=10),),
    maximum_interval=settings.FSRS_MAXIMUM_INTERVAL,
    enable_fuzzing=True,
)


def create_new_card() -> dict:
    card = Card()
    return json.loads(card.to_json())


def review_card(card_json: dict, rating_value: int) -> tuple[dict, dict, datetime]:
    card = Card.from_json(json.dumps(card_json))
    rating = Rating(rating_value)
    updated_card, review_log = scheduler.review_card(card, rating)
    return (
        json.loads(updated_card.to_json()),
        json.loads(review_log.to_json()),
        updated_card.due,
    )


def get_retrievability(card_json: dict) -> float:
    card = Card.from_json(json.dumps(card_json))
    return scheduler.get_card_retrievability(card)
