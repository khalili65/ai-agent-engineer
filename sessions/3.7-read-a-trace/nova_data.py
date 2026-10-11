"""Session 3.7: the Nova Travel data and the support agent's three tools. No AI in this file."""

# A small stand-in for the company booking system
BOOKINGS = {
    "NT-4821": {"customer": "Sara", "trip": "Lisbon, 5 nights, flight + hotel", "price": 640.00,
                "status": "flight cancelled by the airline", "days_before_trip": 9},
    "NT-5107": {"customer": "John", "trip": "Rome, 3 nights, hotel only", "price": 380.00,
                "status": "confirmed", "days_before_trip": 30},
    "NT-6190": {"customer": "Lukas", "trip": "Paris, 4 nights, flight + hotel", "price": 910.00,
                "status": "confirmed", "days_before_trip": 10},
}

REFUND_RULES = (
    "1. The airline cancels the flight: full refund. "
    "2. The customer changes their mind more than 14 days before the trip: "
    "the price minus a $50 fee. "
    "3. The customer changes their mind 14 days or less before the trip: no refund."
)

WAITING_FOR_APPROVAL = []  # Daniel's rule: a person approves every refund


def find_booking(booking_id):
    return BOOKINGS.get(booking_id, {"error": "booking not found"})


def get_refund_rules():
    return {"rules": REFUND_RULES}


def prepare_refund(booking_id, amount, reason):
    """Never sends money: it only puts the refund on the list for a person."""
    refund = {"booking_id": booking_id, "amount": amount, "reason": reason,
              "status": "waiting for a person to approve"}
    WAITING_FOR_APPROVAL.append(refund)
    return refund


FUNCTIONS = {"find_booking": find_booking, "get_refund_rules": get_refund_rules,
             "prepare_refund": prepare_refund}

TOOLS = [
    {"type": "function", "function": {
        "name": "find_booking",
        "description": "Look up a Nova Travel booking by its booking ID, like NT-4821.",
        "parameters": {"type": "object",
                       "properties": {"booking_id": {"type": "string"}},
                       "required": ["booking_id"]}}},
    {"type": "function", "function": {
        "name": "get_refund_rules",
        "description": "Get Nova Travel's refund rules. Use it before any refund.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "prepare_refund",
        "description": "Put a refund on the list for a person to approve. It never sends money.",
        "parameters": {"type": "object",
                       "properties": {"booking_id": {"type": "string"},
                                      "amount": {"type": "number", "description": "In dollars."},
                                      "reason": {"type": "string"}},
                       "required": ["booking_id", "amount", "reason"]}}},
]
