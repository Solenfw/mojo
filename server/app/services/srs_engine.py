from datetime import datetime, timedelta


def calculate_next_review(
    quality_score: int, repetitions: int, ease_factor: float, interval: int
) -> dict:
    """
    Implements SuperMemo-2 algorithm.
    Returns dict with updated: ease_factor, interval, repetitions, next_review_date
    """
    if quality_score < 0 or quality_score > 5:
        raise ValueError("Quality score must be between 0 and 5")

    if quality_score >= 3:
        # Correct response
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)

        new_repetitions = repetitions + 1
        new_ease_factor = ease_factor + (0.1 - (5 - quality_score) * (0.08 + (5 - quality_score) * 0.02))
        new_ease_factor = max(1.3, new_ease_factor)
    else:
        # Incorrect response
        new_repetitions = 0
        new_interval = 1
        new_ease_factor = ease_factor  # Unchanged

    next_review_date = datetime.utcnow().date() + timedelta(days=new_interval)

    return {
        "ease_factor": new_ease_factor,
        "interval": new_interval,
        "repetitions": new_repetitions,
        "next_review_date": next_review_date,
    }
