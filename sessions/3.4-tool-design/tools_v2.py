"""Session 3.4, version 2: three tools designed for the agent."""
from nova import short_record, raw_record, REFUND_RULES, WAITING_LIST

DETAILED = False  # True: find_booking returns the whole raw record (for the size test)

# 1. The functions
def find_booking(booking_id):
    record = raw_record(booking_id) if DETAILED else short_record(booking_id)
    return record or {"error": f"No booking {booking_id}. Booking IDs look like NT-4821."}

def get_refund_rules():
    return {"rules": REFUND_RULES}

def prepare_refund(booking_id, amount, reason):
    request = {"booking_id": booking_id, "amount": amount, "reason": reason,
               "status": "waiting for a person to approve"}
    WAITING_LIST.append(request)  # no money moves here
    return request

FUNCTIONS = {"find_booking": find_booking, "get_refund_rules": get_refund_rules,
             "prepare_refund": prepare_refund}

# 2. What the model reads: clear names, when to use each tool, strict argument types
TOOLS = [
    {"type": "function", "function": {
        "name": "find_booking",
        "description": "Look up one Nova Travel booking. Use it for any question about a "
                       "booking: price paid, city, dates, flight status. "
                       "Returns the booking in short, plain words.",
        "strict": True,
        "parameters": {"type": "object", "properties": {
            "booking_id": {"type": "string", "pattern": "^NT-[0-9]{4}$",
                           "description": "The booking ID in capitals, like NT-4821. "
                                          "If the customer writes nt 4821 or 4821, use NT-4821."}},
            "required": ["booking_id"], "additionalProperties": False}}},
    {"type": "function", "function": {
        "name": "get_refund_rules",
        "description": "Read the Nova Travel refund rules. Use it before you decide "
                       "if a customer gets money back, and how much.",
        "strict": True,
        "parameters": {"type": "object", "properties": {},
                       "required": [], "additionalProperties": False}}},
    {"type": "function", "function": {
        "name": "prepare_refund",
        "description": "Put a refund on Daniel's waiting list. It never sends money: "
                       "a person approves every refund. Use it only after find_booking "
                       "and get_refund_rules, when the rules allow a refund.",
        "strict": True,
        "parameters": {"type": "object", "properties": {
            "booking_id": {"type": "string", "pattern": "^NT-[0-9]{4}$",
                           "description": "Like NT-4821."},
            "amount": {"type": "number", "description": "Refund in US dollars, like 330."},
            "reason": {"type": "string", "enum": ["airline_cancelled", "changed_mind"]}},
            "required": ["booking_id", "amount", "reason"], "additionalProperties": False}}},
]
