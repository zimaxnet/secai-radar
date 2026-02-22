import math
from datetime import datetime, timezone, timedelta
from src.constants.attestation import calculate_decayed_score, EvidenceClass

def test_calculate_decayed_score_class_a():
    """Test Immutable Truth (A) decay - very slow"""
    base = 100.0
    now = datetime.now(timezone.utc)
    
    # Day 0
    score = calculate_decayed_score(base, EvidenceClass.IMMUTABLE_TRUTH, now, now)
    assert score == 100.0
    
    # Day 7 (expected: 100 * e^(-0.01 * 7) = ~93.24)
    past_7 = now - timedelta(days=7)
    score_7 = calculate_decayed_score(base, EvidenceClass.IMMUTABLE_TRUTH, past_7, now)
    assert score_7 == round(100.0 * math.exp(-0.01 * 7), 2)
    assert score_7 == 93.24
    
    # Day 30 (expected: 100 * e^(-0.01 * 30) = ~74.08)
    past_30 = now - timedelta(days=30)
    score_30 = calculate_decayed_score(base, EvidenceClass.IMMUTABLE_TRUTH, past_30, now)
    assert score_30 == round(100.0 * math.exp(-0.01 * 30), 2)
    assert score_30 == 74.08


def test_calculate_decayed_score_class_b():
    """Test Ephemeral Stream (B) decay - moderate"""
    base = 100.0
    now = datetime.now(timezone.utc)
    
    # Day 7 (expected: 100 * e^(-0.50 * 7) = ~3.02)
    past_7 = now - timedelta(days=7)
    score_7 = calculate_decayed_score(base, EvidenceClass.EPHEMERAL_STREAM, past_7, now)
    assert score_7 == round(100.0 * math.exp(-0.50 * 7), 2)
    assert score_7 == 3.02


def test_calculate_decayed_score_class_c():
    """Test Operational Pulse (C) decay - fast"""
    base = 100.0
    now = datetime.now(timezone.utc)
    
    # Day 7 (expected: 100 * e^(-0.90 * 7) = ~0.18)
    past_7 = now - timedelta(days=7)
    score_7 = calculate_decayed_score(base, EvidenceClass.OPERATIONAL_PULSE, past_7, now)
    assert score_7 == round(100.0 * math.exp(-0.90 * 7), 2)


def test_calculate_decayed_score_unknown_class():
    """Test unknown class defaults to 0 decay rate"""
    base = 100.0
    now = datetime.now(timezone.utc)
    past_7 = now - timedelta(days=7)
    
    score = calculate_decayed_score(base, "UNKNOWN_CLASS", past_7, now)
    assert score == 100.0

