import random
import re

from app.schemas.review import (
    FillBlankMCQData,
    FillBlankTypeData,
    MCQData,
    MatchingData,
    MatchingPair,
    OddOneOutData,
    ReverseMCQData,
    ReviewItem,
    TrueFalseData,
    WordInContextData,
)
from app.schemas.word import WordCard


def sample_distractors(
    pool: list[WordCard], exclude_id: int, count: int = 3
) -> list[WordCard]:
    candidates = [w for w in pool if w.id != exclude_id]
    return random.sample(candidates, min(count, len(candidates)))


def build_mcq_item(
    word: WordCard, user_word_id: int, pool: list[WordCard]
) -> ReviewItem:
    distractors = sample_distractors(pool, word.id, count=3)
    options = [word] + distractors
    random.shuffle(options)
    correct_index = next(i for i, o in enumerate(options) if o.id == word.id)
    masked_word = word.model_copy(update={
        "definition": _mask_word(word.definition, word.word) if word.definition else word.definition,
    })
    return ReviewItem(
        type="multiple_choice",
        user_word_id=user_word_id,
        word=masked_word,
        mcq_data=MCQData(options=options, correct_index=correct_index),
    )


def build_reverse_mcq_item(
    word: WordCard, user_word_id: int, pool: list[WordCard]
) -> ReviewItem:
    distractors = sample_distractors(pool, word.id, count=3)
    correct_def = _mask_word(
        word.definition or word.translation_ru or "—", word.word
    )
    distractor_defs = [
        _mask_word(d.definition or d.translation_ru or "—", d.word)
        for d in distractors
    ]
    all_defs = [correct_def] + distractor_defs
    indices = list(range(len(all_defs)))
    random.shuffle(indices)
    shuffled = [all_defs[i] for i in indices]
    correct_index = indices.index(0)
    return ReviewItem(
        type="reverse_mcq",
        user_word_id=user_word_id,
        word=word,
        reverse_mcq_data=ReverseMCQData(
            definition_options=shuffled, correct_index=correct_index
        ),
    )


def _mask_word(text: str, word: str) -> str:
    pattern = re.compile(re.escape(word), re.IGNORECASE)
    return pattern.sub("___", text)


def _blank_word_in_sentence(sentence: str, word: str) -> str:
    return _mask_word(sentence, word)


def build_fill_blank_mcq_item(
    word: WordCard, user_word_id: int, pool: list[WordCard]
) -> ReviewItem:
    sentence = _blank_word_in_sentence(word.example_sentence, word.word)
    distractors = sample_distractors(pool, word.id, count=3)
    options = [word.word] + [d.word for d in distractors]
    random.shuffle(options)
    correct_index = options.index(word.word)
    return ReviewItem(
        type="fill_blank_mcq",
        user_word_id=user_word_id,
        word=word,
        fill_blank_mcq_data=FillBlankMCQData(
            sentence_with_blank=sentence,
            options=options,
            correct_index=correct_index,
        ),
    )


def build_fill_blank_type_item(
    word: WordCard, user_word_id: int
) -> ReviewItem:
    sentence = _blank_word_in_sentence(word.example_sentence, word.word)
    return ReviewItem(
        type="fill_blank_type",
        user_word_id=user_word_id,
        word=word,
        fill_blank_type_data=FillBlankTypeData(
            sentence_with_blank=sentence,
            correct_answer=word.word.lower(),
        ),
    )


def build_matching_item(
    word_pairs: list[tuple[int, WordCard]],
) -> ReviewItem:
    pairs = [
        MatchingPair(
            user_word_id=uw_id,
            word=wc.word,
            definition=_mask_word(
                wc.definition or wc.translation_ru or "—", wc.word
            ),
        )
        for uw_id, wc in word_pairs
    ]
    return ReviewItem(
        type="matching",
        matching_data=MatchingData(pairs=pairs),
    )


def build_odd_one_out_item(
    word: WordCard,
    user_word_id: int,
    synonym_words: list[str],
    odd_word: str,
) -> ReviewItem:
    related = [word.word] + synonym_words[:2]
    words = related + [odd_word]
    random.shuffle(words)
    odd_index = words.index(odd_word)
    return ReviewItem(
        type="odd_one_out",
        user_word_id=user_word_id,
        word=word,
        odd_one_out_data=OddOneOutData(words=words, odd_index=odd_index),
    )


def build_true_false_item(
    word: WordCard, user_word_id: int, pool: list[WordCard]
) -> ReviewItem:
    show_correct = random.random() < 0.5
    if show_correct:
        shown_def = _mask_word(
            word.definition or word.translation_ru or "—", word.word
        )
    else:
        candidates = [d for d in pool if d.id != word.id and d.definition]
        if candidates:
            wrong = random.choice(candidates)
            shown_def = _mask_word(wrong.definition, word.word)
        else:
            shown_def = _mask_word(
                word.definition or word.translation_ru or "—", word.word
            )
            show_correct = True
    return ReviewItem(
        type="true_false",
        user_word_id=user_word_id,
        word=word,
        true_false_data=TrueFalseData(
            shown_definition=shown_def, is_correct_pair=show_correct
        ),
    )


def build_word_in_context_item(
    word: WordCard, user_word_id: int, pool: list[WordCard]
) -> ReviewItem:
    correct_def = _mask_word(
        word.definition or word.translation_ru or "—", word.word
    )
    candidates = [d for d in pool if d.id != word.id and d.definition]
    selected = random.sample(candidates, min(3, len(candidates)))
    definitions = [correct_def] + [
        _mask_word(d.definition, word.word) for d in selected
    ]
    indices = list(range(len(definitions)))
    random.shuffle(indices)
    shuffled = [definitions[i] for i in indices]
    correct_index = indices.index(0)
    return ReviewItem(
        type="word_in_context",
        user_word_id=user_word_id,
        word=word,
        word_in_context_data=WordInContextData(
            sentence=word.example_sentence,
            definition_options=shuffled,
            correct_index=correct_index,
        ),
    )
