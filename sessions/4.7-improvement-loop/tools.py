"""Tools for the support agent (a copy of Lab 1): plain Python functions the model may ask for.

Every tool returns a small dict. When something is wrong, the tool does not crash:
it returns {"error": ...} with a hint that tells the model what to do next.
"""
import json
from pathlib import Path

DATA = Path(__file__).parent / "data"
BOOKINGS = json.loads((DATA / "bookings.json").read_text())

# Daniel's rule: the agent never sends money. Refunds and changes only wait here
# until a person on the team approves them.
WAITING_LIST: list[dict] = []
WAITING = "waiting for a person to approve"


def find_booking(booking_id: str) -> dict:
    """Look up one booking in the company system."""
    booking_id = booking_id.strip().upper()
    if booking_id not in BOOKINGS:
        return {"error": f"No booking with the ID {booking_id}.",
                "hint": "IDs look like NT-4821. Ask the customer to check the number. Never guess it."}
    return {"booking_id": booking_id, **BOOKINGS[booking_id]}


def get_refund_rules() -> dict:
    """Read the company refund rules."""
    return {"rules": (DATA / "rules.md").read_text()}


def get_policy(topic: str) -> dict:
    """Read one part of the travel policy: baggage, changes or cancellations."""
    sections = (DATA / "policy.md").read_text().split("## ")[1:]
    policy = {s.split("\n", 1)[0].strip(): s.split("\n", 1)[1].strip() for s in sections}
    if topic not in policy:
        return {"error": f"No policy topic called {topic!r}.",
                "hint": f"Use one of these topics: {', '.join(policy)}."}
    return {"topic": topic, "policy": policy[topic]}


def refund_amount(booking: dict, reason: str) -> float:
    """The refund rules, written as code. Returns 0 when there is no refund."""
    if reason == "airline_cancelled":
        return booking["price"] if booking["flight"] == "cancelled by the airline" else 0
    if reason == "changed_mind" and booking["days_before_trip"] > 14:
        return booking["price"] - 50
    return 0


def prepare_refund(booking_id: str, amount: float, reason: str) -> dict:
    """Put a refund on the waiting list. It sends NO money: a person approves it first."""
    booking = find_booking(booking_id)
    if "error" in booking:
        return booking
    allowed = refund_amount(booking, reason)
    if allowed == 0:
        return {"error": f"No refund for {booking['booking_id']} with the reason {reason}.",
                "hint": f"The trip is in {booking['days_before_trip']} days and the flight is "
                        f"{booking['flight']}. Read the refund rules again and explain them "
                        "to the customer. Do not prepare a refund."}
    if amount != allowed:
        return {"error": f"The refund for {booking['booking_id']} must be {allowed}, not {amount}.",
                "hint": "Call prepare_refund again with the right amount."}
    refund = {"kind": "refund", "booking_id": booking["booking_id"], "amount": amount,
              "reason": reason, "status": WAITING}
    WAITING_LIST.append(refund)
    return refund


def get_refund_status(booking_id: str) -> dict:
    """New in session 4.7: show the refunds that already wait on the list for this booking."""
    booking_id = booking_id.strip().upper()
    refunds = [item for item in WAITING_LIST if item["kind"] == "refund" and item["booking_id"] == booking_id]
    if not refunds:
        return {"booking_id": booking_id, "refunds": [], "note": "No refund for this booking is on the list."}
    return {"booking_id": booking_id, "refunds": refunds,
            "note": "Only a person decides if and when a refund is approved. After approval, "
                    "the money reaches the card in 5 to 10 working days."}


def change_fee(booking: dict) -> float:
    """The change policy, written as code: free more than 7 days before the trip, else 30 dollars."""
    return 0 if booking["days_before_trip"] > 7 else 30


def prepare_change(booking_id: str, change: str, fee: float) -> dict:
    """Put a booking change on the waiting list. A person confirms it with the hotel or airline."""
    booking = find_booking(booking_id)
    if "error" in booking:
        return booking
    if fee != change_fee(booking):
        return {"error": f"The change fee for {booking['booking_id']} is {change_fee(booking)}, not {fee}.",
                "hint": "Read the changes policy, then call prepare_change again with the right fee."}
    request = {"kind": "change", "booking_id": booking["booking_id"], "change": change,
               "fee": fee, "status": WAITING}
    WAITING_LIST.append(request)
    return request


# The dispatch table: the name the model uses -> the Python function we run.
TOOLS = {
    "find_booking": find_booking,
    "get_refund_rules": get_refund_rules,
    "get_policy": get_policy,
    "prepare_refund": prepare_refund,
    "prepare_change": prepare_change,
    "get_refund_status": get_refund_status,
}

# What the model sees about each tool: name, description, input.
TOOL_SPECS = [
    {"name": "find_booking",
     "description": "Look up a Nova Travel booking by its ID, like NT-4821.",
     "parameters": {"type": "object",
                    "properties": {"booking_id": {"type": "string"}},
                    "required": ["booking_id"]}},
    {"name": "get_refund_rules",
     "description": "Read the Nova Travel refund rules. Read them before you work out any refund.",
     "parameters": {"type": "object", "properties": {}}},
    {"name": "get_policy",
     "description": "Read the travel policy on one topic.",
     "parameters": {"type": "object",
                    "properties": {"topic": {"type": "string",
                                             "enum": ["baggage", "changes", "cancellations"]}},
                    "required": ["topic"]}},
    {"name": "prepare_refund",
     "description": "Put a refund on the waiting list for a person to approve. It does not send money.",
     "parameters": {"type": "object",
                    "properties": {"booking_id": {"type": "string"},
                                   "amount": {"type": "number", "description": "dollars"},
                                   "reason": {"type": "string",
                                              "enum": ["airline_cancelled", "changed_mind"]}},
                    "required": ["booking_id", "amount", "reason"]}},
    {"name": "prepare_change",
     "description": "Put a date change on the waiting list for a person to confirm.",
     "parameters": {"type": "object",
                    "properties": {"booking_id": {"type": "string"},
                                   "change": {"type": "string", "description": "what to change"},
                                   "fee": {"type": "number", "description": "change fee in dollars"}},
                    "required": ["booking_id", "change", "fee"]}},
    {"name": "get_refund_status",
     "description": "See the refunds that already wait for a person to approve them, for one booking. "
                    "Use it when a customer asks about a refund they asked for before.",
     "parameters": {"type": "object",
                    "properties": {"booking_id": {"type": "string"}},
                    "required": ["booking_id"]}},
]

# The five tools of the support agent v1 (Lab 1).
V1_TOOLS = ["find_booking", "get_refund_rules", "get_policy", "prepare_refund", "prepare_change"]
# Version 2 adds one tool: the agent can now see the refunds that already wait.
V2_TOOLS = V1_TOOLS + ["get_refund_status"]
