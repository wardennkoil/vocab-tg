import random

from app.schemas.word import WordCard

TYPE_WEIGHTS = {
    "multiple_choice": 20,
    "reverse_mcq": 20,
    "fill_blank_mcq": 15,
    "fill_blank_type": 10,
    "odd_one_out": 10,
    "true_false": 15,
    "word_in_context": 10,
}


def get_eligible_types(word: WordCard, has_synonym_group: bool) -> list[str]:
    eligible = []

    if word.definition or word.translation_ru:
        eligible.append("multiple_choice")

    if word.definition:
        eligible.append("reverse_mcq")

    has_fill_blank = (
        word.example_sentence
        and word.word.lower() in word.example_sentence.lower()
    )
    if has_fill_blank:
        eligible.append("fill_blank_mcq")
        eligible.append("fill_blank_type")

    if has_synonym_group:
        eligible.append("odd_one_out")

    if word.definition:
        eligible.append("true_false")

    if word.example_sentence and word.definition:
        eligible.append("word_in_context")

    return eligible if eligible else ["multiple_choice"]


def select_review_type(word: WordCard, has_synonym_group: bool) -> str:
    eligible = get_eligible_types(word, has_synonym_group)
    weights = [TYPE_WEIGHTS.get(t, 10) for t in eligible]
    return random.choices(eligible, weights=weights, k=1)[0]
