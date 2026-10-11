"""Session 3.5: a small stand-in for the Nova Travel booking system, and the support agent's tools.

The other files in this folder import from here. Every tool can fail, like real systems do.
"""
import re
import time

BOOKINGS = {
    "NT-4821": {"customer": "Sara", "trip": "Lisbon, 5 nights, flight + hotel", "price": 640.0,
                "flight": "cancelled by the airline", "days_before_trip": 9,
                "refund": "640.00 dollars, waiting for a person to approve"},
    "NT-5107": {"customer": "John", "trip": "Rome, 3 nights, hotel only", "price": 380.0,
                "flight": "none", "days_before_trip": 30},
    "NT-5512": {"customer": "Emma", "trip": "Barcelona, 4 nights, hotel only", "price": 420.0,
                "flight": "none", "days_before_trip": 21},
    "NT-6190": {"customer": "Lukas", "trip": "Paris, 3 nights, flight + hotel", "price": 560.0,
                "flight": "on time", "days_before_trip": 40},
}

REFUND_RULES = (
    "If the airline cancels the flight, the customer gets a full refund. "
    "If the customer changes their mind more than 14 days before the trip, "
    "they get the price minus a 50 dollar fee. "
    "If they change their mind 14 days or less before the trip, there is no refund. "
    "A person approves every refund before any money is sent."
)

WAITING_LIST = []  # refunds waiting for a person to approve (Daniel's rule)
FOR_A_PERSON = []  # customer messages the agent hands to a person
SYSTEM = {"slow_calls": 0}  # how many of the next lookups time out (to act like a slow system)


def find_booking(booking_id):
    """Look up a booking. Raises an error with a clear message when something is wrong."""
    if SYSTEM["slow_calls"] > 0:  # the booking system is slow right now
        SYSTEM["slow_calls"] -= 1
        time.sleep(0.5)
        raise TimeoutError("The booking system did not answer in time.")
    if re.fullmatch(r"\d{4}", booking_id):  # four digits, but no NT- in front
        raise ValueError(f"{booking_id} is missing NT- in front. "
                         f"Call find_booking again with NT-{booking_id}.")
    if booking_id not in BOOKINGS:
        raise LookupError(
            f"No booking {booking_id}. Booking numbers look like NT- and four digits, "
            "for example NT-4821. If the customer's number is not complete, "
            "ask the customer to check it. Never guess digits.")
    return BOOKINGS[booking_id]


def get_refund_rules():
    return REFUND_RULES


def prepare_refund(booking_id, amount, reason):
    """Only adds the refund to the waiting list. It never sends money."""
    booking = find_booking(booking_id)
    if amount > booking["price"]:
        raise ValueError(f"The amount {amount} is more than the price of the trip, "
                         f"{booking['price']}. Check the refund rules and the price.")
    refund = {"booking_id": booking_id, "amount": amount, "reason": reason,
              "status": "waiting for a person to approve"}
    WAITING_LIST.append(refund)
    return refund


TOOL_FUNCTIONS = {"find_booking": find_booking, "get_refund_rules": get_refund_rules,
                  "prepare_refund": prepare_refund}

TOOLS = [
    {"type": "function", "function": {
        "name": "find_booking", "description": "Look up a Nova Travel booking by its booking ID.",
        "parameters": {"type": "object", "properties": {"booking_id": {"type": "string"}},
                       "required": ["booking_id"]}}},
    {"type": "function", "function": {
        "name": "get_refund_rules", "description": "Read the Nova Travel refund rules.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "prepare_refund",
        "description": "Put a refund on the waiting list for a person to approve. It does not send money.",
        "parameters": {"type": "object", "properties": {
            "booking_id": {"type": "string"}, "amount": {"type": "number"},
            "reason": {"type": "string"}}, "required": ["booking_id", "amount", "reason"]}}},
]

SYSTEM_PROMPT = ("You are the Nova Travel support agent. Check facts with your tools. "
                 "Keep going until the customer's question is fully answered. "
                 "You never send money yourself; a person approves every refund. "
                 "Answer in two or three short sentences.")

CUSTOMERS = {
    "emma": "Hi, this is Emma. My hotel in Barcelona starts in three weeks, but I changed "
            "my mind. Can I cancel and get my money back? My booking is NT-512.",
    "emma2": "Sorry, my mistake! The right booking number is NT-5512.",
    "emma3": "Yes, please prepare the refund.",
    "lukas": "Hi, Lukas here, booking 6190. Is my flight to Paris still on time?",
    "sara": "Hi, it's Sara again, booking NT-4821. Has my refund for Lisbon been approved yet?",
}
