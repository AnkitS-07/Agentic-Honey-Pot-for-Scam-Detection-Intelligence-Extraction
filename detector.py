from transformers import pipeline
from typing import Tuple
import os

IS_RENDER = os.getenv("RENDER", "").lower() == "true"

_detector = None


def get_detector():
    global _detector
    if _detector is None:
        _detector = pipeline(
            "text-classification",
            model="cybersectony/phishing-email-detection-distilbert_v2.1",
            truncation=True,
            device=-1
        )
    return _detector


SUSPICIOUS_KEYWORDS = [
    "urgent",
    "verify",
    "account",
    "blocked",
    "suspended",
    "kyc",
    "refund",
    "debit",
    "credit",
    "bank",
    "upi",
    "money",
]

STRONG_KEYWORDS = {
    "otp",
    "upi pin",
    "pin",
    "one time password",
}


def detect_scam(text: str) -> Tuple[bool, float]:
    text = text.lower()

    if IS_RENDER:
        if any(sk in text for sk in STRONG_KEYWORDS):
            return True, 0.9

        hits = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in text)
        if hits >= 2:
            return True, 0.7

        return False, 0.0

    detector = get_detector()
    result = detector(text, max_length=512)[0]

    label = result["label"].lower()
    score = float(result["score"])

    is_scam = "phish" in label or "spam" in label or "fraud" in label

    if any(sk in text for sk in STRONG_KEYWORDS):
        is_scam = True
        score = max(score, 0.85)

    if sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in text) >= 2:
        is_scam = True
        score = max(score, 0.6)

    return is_scam, score if is_scam else 0.0
