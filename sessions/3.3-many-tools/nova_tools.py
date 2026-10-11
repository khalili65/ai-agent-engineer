"""Session 3.3: the support agent's tools, their descriptions, and the dispatch table."""

# A small stand-in for the Nova Travel booking system
BOOKINGS = {
    "NT-4821": {"customer": "Sara", "trip": "Lisbon, 5 nights, flight + hotel",
                "price": 640.0, "flight": "cancelled by the airline", "days_before_trip": 9},
    "NT-5107": {"customer": "John", "trip": "Rome, 3 nights, hotel only",
                "price": 380.0, "flight": "none", "days_before_trip": 30},
    "NT-7012": {"customer": "Maria", "trip": "Porto, 2 nights, hotel only",
                "price": 290.0, "flight": "none", "days_before_trip": 10},
    "NT-7013": {"customer": "Maria", "trip": "Barcelona, 7 nights, flight + hotel, 4 people",
                "price": 1480.0, "flight": "on time", "days_before_trip": 40},
}

REFUND_RULES = [
    "If the airline cancels the flight, the customer gets a full refund.",
    "If the customer changes their mind more than 14 days before the trip, "
    "they get the price minus a 50 dollar fee.",
    "If the customer changes their mind 14 days or less before the trip, there is no refund.",
]

WAITING_LIST = []  # Daniel's list: a person approves every refund


# 1. The tools: normal Python functions
def find_booking(booking_id):
    return BOOKINGS.get(booking_id, {"error": "booking not found"})

def get_refund_rules():
    return {"rules": REFUND_RULES}

def prepare_refund(booking_id, amount, reason):
    request = {"booking_id": booking_id, "amount": amount, "reason": reason,
               "status": "waiting for a person to approve"}
    WAITING_LIST.append(request)  # no money moves here
    return request


# 2. The dispatch table: tool name -> function
TOOL_FUNCTIONS = {
    "find_booking": find_booking,
    "get_refund_rules": get_refund_rules,
    "prepare_refund": prepare_refund,
}

def run_tool(name, args):
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return {"error": f"unknown tool: {name}"}
    return function(**args)


# 3. The tool descriptions the model reads
TOOLS = [
    {"type": "function", "function": {
        "name": "find_booking",
        "description": "Look up one Nova Travel booking by its booking ID.",
        "parameters": {"type": "object",
                       "properties": {"booking_id": {"type": "string"}},
                       "required": ["booking_id"]}}},
    {"type": "function", "function": {
        "name": "get_refund_rules",
        "description": "Read the Nova Travel refund rules.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "prepare_refund",
        "description": "Put a refund on Daniel's waiting list. It never sends money; "
                       "a person approves every refund.",
        "parameters": {"type": "object",
                       "properties": {"booking_id": {"type": "string"},
                                      "amount": {"type": "number"},
                                      "reason": {"type": "string"}},
                       "required": ["booking_id", "amount", "reason"]}}},
]

SYSTEM = ("You are the Nova Travel support agent. Check facts with your tools. "
          "Read the refund rules before you decide about a refund. "
          "If the customer asks for a refund and the rules allow it, "
          "use prepare_refund right away. "
          "You never send money; a person approves every refund. "
          "Answer in short, simple sentences.")

MARIA = ("Hi, this is Maria. I have two bookings with you, NT-7012 and NT-7013. "
         "I just started a new job, and I cannot travel this year. "
         "Can I get my money back for both trips?")
