import pandas as pd
import pytest

from src.generate_sample import generate_transactions
from src.pipeline import build_review_queue


def test_review_queue_is_ranked_and_explainable():
    queue = build_review_queue(generate_transactions(rows=200))
    assert queue["risk_score"].is_monotonic_decreasing
    assert queue["risk_reason"].str.len().gt(0).all()
    assert set(queue["risk_band"]).issubset({"low", "medium", "high"})


def test_validation_rejects_duplicate_ids():
    frame = generate_transactions(rows=10)
    frame.loc[1, "transaction_id"] = frame.loc[0, "transaction_id"]
    with pytest.raises(ValueError, match="unique"):
        build_review_queue(frame)


def test_validation_rejects_non_positive_amount():
    frame = generate_transactions(rows=10)
    frame.loc[0, "amount"] = 0
    with pytest.raises(ValueError, match="positive"):
        build_review_queue(frame)
