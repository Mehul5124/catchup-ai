"""
security.py – PII Redaction & Role-Based Masking for CatchUp AI
"""

import re
import copy
from typing import Any


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# US phone:  XXX-XXX-XXXX  or  (XXX) XXX-XXXX  or  XXX.XXX.XXXX
_PHONE_RE = re.compile(
    r"\b(?:\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4})\b"
)

# Email address
_EMAIL_RE = re.compile(
    r"\b([A-Za-z0-9._%+\-]+)(@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})\b"
)

# Credit card: XXXX-XXXX-XXXX-XXXX (with dashes or spaces)
_CC_RE = re.compile(
    r"\b(\d{4})[\s\-](\d{4})[\s\-](\d{4})[\s\-](\d{4})\b"
)

# Financial numbers (amounts like $250,000 or 2.5M)
_FINANCIAL_RE = re.compile(
    r"\$[\d,]+(?:\.\d+)?(?:[KkMmBb])?\b|\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|thousand|[KkMmBb])\b",
    re.IGNORECASE,
)

# Personal email domains (not company domains)
_PERSONAL_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@(?:gmail|yahoo|hotmail|outlook|proton|icloud|aol)\.(?:com|net|org)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Core PII redaction
# ---------------------------------------------------------------------------

def redact_pii(text: str) -> str:
    """
    Scan *text* and mask sensitive PII:
      - Phone numbers  →  [PHONE REDACTED]
      - Email addresses → user***@domain.com
      - Credit card numbers → XXXX-****-****-XXXX
    Returns the sanitised string.
    """
    if not isinstance(text, str):
        return text

    # Credit cards first (more specific pattern)
    text = _CC_RE.sub(r"\1-****-****-\4", text)

    # Phone numbers
    text = _PHONE_RE.sub("[PHONE REDACTED]", text)

    # Email: keep first part partially, keep domain
    def _mask_email(m: re.Match) -> str:
        user = m.group(1)
        domain = m.group(2)
        if len(user) <= 3:
            masked = user[0] + "***"
        else:
            masked = user[:3] + "***"
        return masked + domain

    text = _EMAIL_RE.sub(_mask_email, text)

    return text


# ---------------------------------------------------------------------------
# Role-based masking
# ---------------------------------------------------------------------------

def mask_for_role(data: Any, role: str) -> Any:
    """
    Apply role-based masking to *data* before sending to Gemini.

    - role='manager'  → full data, only basic PII redaction (phones, CC)
    - role='employee' → additionally masks financial numbers and personal emails
    """
    # Deep copy so we don't mutate the original
    data = copy.deepcopy(data)

    if role == "manager":
        return _apply_manager_mask(data)
    else:
        return _apply_employee_mask(data)


def _apply_manager_mask(data: Any) -> Any:
    """Manager view: redact CC and phones only."""
    return _walk_and_redact(data, _redact_manager)


def _apply_employee_mask(data: Any) -> Any:
    """Employee view: also mask financial figures and personal emails."""
    return _walk_and_redact(data, _redact_employee)


def _redact_manager(text: str) -> str:
    """Mask CC and phones for manager view."""
    text = _CC_RE.sub(r"\1-****-****-\4", text)
    text = _PHONE_RE.sub("[PHONE REDACTED]", text)
    return text


def _redact_employee(text: str) -> str:
    """Mask CC, phones, financials, and personal emails for employee view."""
    text = _redact_manager(text)
    text = _FINANCIAL_RE.sub("[AMOUNT REDACTED]", text)
    text = _PERSONAL_EMAIL_RE.sub("[PERSONAL EMAIL REDACTED]", text)
    return text


def _walk_and_redact(obj: Any, redact_fn) -> Any:
    """Recursively walk a dict/list/str and apply redact_fn to all strings."""
    if isinstance(obj, str):
        return redact_fn(obj)
    elif isinstance(obj, dict):
        return {k: _walk_and_redact(v, redact_fn) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_walk_and_redact(item, redact_fn) for item in obj]
    return obj


# ---------------------------------------------------------------------------
# Quick demo / smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample = {
        "message": (
            "Please call John at 555-867-5309 or email him at john.doe@gmail.com. "
            "The contract is worth $2,500,000. "
            "Payment card: 4111-1234-5678-9012. "
            "Work email: john.doe@company.com"
        ),
        "amount": "Budget: $250k for Q3",
    }

    print("=== Original ===")
    print(sample)

    print("\n=== Manager View ===")
    print(mask_for_role(sample, "manager"))

    print("\n=== Employee View ===")
    print(mask_for_role(sample, "employee"))

    print("\n=== redact_pii() standalone ===")
    print(redact_pii("Contact: 415.555.1234, pay via 4242-4242-4242-4242, reach at admin@example.com"))
