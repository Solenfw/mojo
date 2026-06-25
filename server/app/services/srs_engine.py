import math
from datetime import datetime, timedelta, timezone
from server.app.db.schemas import SRSReviewResult

def process_srs_review(score: int, current_rep: int, current_ef: float, current_interval: int) -> SRSReviewResult:
    """
    Refactored SM-2 Spaced Repetition Algorithm.
    Fixes the 'hell-loop' flaw by guarding the EF minimum floor at 1.3
    and scaling intervals conditionally based on quality scores.
    """
    # If the user failed to recall the word or found it completely unfamiliar (Score < 3)
    if score < 3:
        # Instead of resetting completely, reduce EF slightly and set interval back to 1 day
        new_ef = max(1.3, current_ef - 0.2)
        return SRSReviewResult(
            repetitions=0,
            easiness_factor=round(new_ef, 2),
            interval_days=1,
            next_review=datetime.now(timezone.utc) + timedelta(days=1)
        )
    
    # If the card was correctly recalled (Score >= 3)
    if current_rep == 0:
        new_interval = 1
    elif current_rep == 1:
        new_interval = 6
    else:
        new_interval = math.ceil(current_interval * current_ef)
        
    # Standard SuperMemo SM-2 formula for EF adjustment
    new_ef = current_ef + (0.1 - (5 - score) * (0.08 + (5 - score) * 0.02))
    new_ef = max(1.3, new_ef)  # Hard structural floor guard
    
    return SRSReviewResult(
        repetitions=current_rep + 1,
        easiness_factor=round(new_ef, 2),
        interval_days=new_interval,
        next_review=datetime.now(timezone.utc) + timedelta(days=new_interval)
    )