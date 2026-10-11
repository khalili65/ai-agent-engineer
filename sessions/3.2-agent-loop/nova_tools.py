"""Session 3.2: the support agent's three tools and their descriptions.

The tools are normal Python functions. They are small stand-ins for the Nova Travel system.
"""

BOOKINGS = {
    "NT-4821": {"customer": "Sara", "trip": "Lisbon, 5 nights, flight + hotel",
                "price": 640.00, "days_before_trip": 9, "flight": "cancelled by the airline"},
    "NT-5107": {"customer": "John", "trip": "Rome, 3 nights, hotel only",
                "price": 380.00, "days_before_trip": 30, "flight": "none"},
}

REFUND_RULES = [
    "The airline cancels the flight: full refund.",
    "The customer changes their mind more than 14 days before the trip: price minus $50.",
    "The customer changes their mind 14 days or less before the trip: no refund.",
]

# Daniel's rule: the agent never sends money. It only adds a request to this list,
# and a person approves every refund.
WAITING_LIST = []


def find_booking(booking_id):
    return BOOKINGS.get(booking_id, {"error": "booking not found"})


def get_refund_rules():
    return {"rules": REFUND_RULES}


def prepare_refund(booking_id, amount, reason):
    request = {"booking_id": booking_id, "amount": amount, "reason": reason,
               "status": "waiting for a person to approve"}
    WAITING_LIST.append(request)
    return request


# The functions our code may run, by name.
FUNCTIONS = {"find_booking": find_booking,
             "get_refund_rules": get_refund_rules,
             "prepare_refund": prepare_refund}

# What the model knows about the tools: name, what it does, its input.
TOOLS = [
    {"type": "function", "function": {
        "name": "find_booking",
        "description": "Look up a Nova Travel booking by its booking ID, like NT-4821.",
        "parameters": {"type": "object",
                       "properties": {"booking_id": {"type": "string"}},
                       "required": ["booking_id"]}}},
    {"type": "function", "function": {
        "name": "get_refund_rules",
        "description": "Get the Nova Travel refund rules.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "prepare_refund",
        "description": "Prepare a refund request. It does not send money: "
                       "it puts the request on the list for a person to approve.",
        "parameters": {"type": "object",
                       "properties": {"booking_id": {"type": "string"},
                                      "amount": {"type": "number"},
                                      "reason": {"type": "string"}},
                       "required": ["booking_id", "amount", "reason"]}}},
]

SYSTEM = ("You are the Nova Travel support agent. Check every fact with your tools: "
          "find the booking, read the refund rules, and prepare the refund if the rules allow it. "
          "You never send money yourself; a person approves every refund. "
          "Answer the customer in two or three short sentences.")

SARA = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
        "My booking is NT-4821. Can I get my money back?")

# A customer who lost the booking number (used in lost_number.py and token_budget.py).
EMMA = ("Hi, this is Emma. I changed my mind about my trip to Barcelona in December. "
        "I lost my booking number, I only remember that it starts with NT-73. "
        "Can I get my money back?")
