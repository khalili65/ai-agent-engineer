"""Tools for the support agent: plain Python functions the model may ask for."""
import json
from pathlib import Path

DATA = Path(__file__).parent / "data"
BOOKINGS = json.loads((DATA / "bookings.json").read_text())
PENDING_REFUNDS: list[dict] = []  # refunds waiting for a person to approve


def find_booking(booking_id: str) -> dict:
    """Look up a booking in the company system."""
    return BOOKINGS.get(booking_id, {"error": "booking not found"})


def get_refund_rules() -> str:
    """Read the company refund rules."""
    return (DATA / "rules.md").read_text()


def prepare_refund(booking_id: str, amount: float, reason: str) -> dict:
    """Prepare a refund. It is NOT sent: a person must approve it first (Daniel's rule)."""
    if booking_id not in BOOKINGS:
        return {"error": "booking not found"}
    refund = {"booking_id": booking_id, "amount": amount, "reason": reason, "status": "waiting for approval"}
    PENDING_REFUNDS.append(refund)
    return refund


TOOLS = {"find_booking": find_booking, "get_refund_rules": get_refund_rules, "prepare_refund": prepare_refund}

TOOL_DESCRIPTIONS = [
    {"type": "function", "function": {"name": "find_booking", "description": "Look up a Nova Travel booking by its booking ID.",
     "parameters": {"type": "object", "properties": {"booking_id": {"type": "string"}}, "required": ["booking_id"]}}},
    {"type": "function", "function": {"name": "get_refund_rules", "description": "Read the Nova Travel refund rules.",
     "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "prepare_refund", "description": "Prepare a refund for a person to approve. It does not send money.",
     "parameters": {"type": "object", "properties": {"booking_id": {"type": "string"}, "amount": {"type": "number"},
                    "reason": {"type": "string"}}, "required": ["booking_id", "amount", "reason"]}}},
]
