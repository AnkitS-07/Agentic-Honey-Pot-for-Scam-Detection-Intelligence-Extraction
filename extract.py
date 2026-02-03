import re
from typing import Dict, List

# Regex patterns (India-focused)
BANK_ACCOUNT_PATTERN = re.compile(r"\b\d{9,18}\b")

UPI_PATTERN = re.compile(
    r"\b[a-zA-Z0-9.\-_]{3,}@[a-zA-Z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?:\+91[-\s]?|0)?[6-9]\d{9}\b"
)

URL_PATTERN = re.compile(
    r"https?://[^\s\"'>]+"
)

SUSPICIOUS_KEYWORDS = frozenset({
    "otp", "upi", "bank", "verify", "blocked", "urgent", "suspended",
    "kyc", "pin", "refund", "gift card", "crypto", "bitcoin", "btc",
    "gold", "money",
})

def _normalize_number(num: str) -> str:
    """Keep only digits for comparison."""
    return re.sub(r"\D", "", num)


def extract_intelligence(text: str) -> Dict[str, List[str]]:
    """
    Extract scam-related intelligence with proper normalization
    and zero overlaps.
    """

    text_lower = text.lower()

    raw_bank_accounts = set(BANK_ACCOUNT_PATTERN.findall(text))
    raw_phone_numbers = set(PHONE_PATTERN.findall(text))
    upi_ids = set(UPI_PATTERN.findall(text))
    urls = set(URL_PATTERN.findall(text))

    # Normalize phone numbers for comparison
    normalized_phones = {
        _normalize_number(p) for p in raw_phone_numbers
    }

    # Remove phone numbers from bank accounts (normalized comparison)
    cleaned_bank_accounts = [
        acc for acc in raw_bank_accounts
        if _normalize_number(acc) not in normalized_phones
    ]

    intelligence = {
        "bankAccounts": cleaned_bank_accounts,
        "upiIds": list(upi_ids),
        "phoneNumbers": list(raw_phone_numbers),
        "phishingLinks": list(urls),
        "suspiciousKeywords": [
            kw for kw in SUSPICIOUS_KEYWORDS if kw in text_lower
        ]
    }

    return intelligence