CEFR_TO_BAND = {
    "A1": "A1-A2",
    "A2": "A1-A2",
    "B1": "B1-B2",
    "B2": "B2-C1",
    "C1": "C1-C2",
    "C2": "C1-C2",
}


def assign_difficulty_band(frequency_rank: int | None) -> str:
    if frequency_rank is None:
        return "C1-C2"
    if frequency_rank <= 1000:
        return "A1-A2"
    elif frequency_rank <= 3000:
        return "B1-B2"
    elif frequency_rank <= 6000:
        return "B2-C1"
    else:
        return "C1-C2"


def cefr_to_difficulty_band(cefr: str) -> str:
    return CEFR_TO_BAND.get(cefr.upper(), "C1-C2")
