"""Session 3.6: the support agent's tools and a small stand-in for the Nova Travel system."""

BOOKINGS = {
    "NT-4821": {"customer": "Sara", "trip": "Lisbon, 5 nights, flight + hotel", "price": 640.0,
                "flight": "cancelled by the airline", "days_before_trip": 9},
    "NT-5602": {"customer": "Anna Weber", "trip": "Barcelona, 4 nights, flight + hotel, family of four",
                "price": 1860.0, "flight": "on time", "days_before_trip": 40},
    "NT-5603": {"customer": "Anna Weber", "trip": "Vienna, 3 nights, hotel only",
                "price": 510.0, "check_in": "June 12", "check_out": "June 15", "days_before_trip": 52},
    "NT-5604": {"customer": "Eva Weber", "trip": "Rome, 5 nights, flight + hotel",
                "price": 720.0, "flight": "cancelled by the airline", "days_before_trip": 6},
}

REFUND_RULES = (
    "If the airline cancels the flight, the customer gets a full refund. "
    "If the customer changes their mind more than 14 days before the trip, "
    "they get the price minus a 50 dollar fee. 14 days or less before the trip: no refund. "
    "A person approves every refund."
)

POLICIES = {
    "pets": "Small dogs up to 10 kg may stay in our Vienna partner hotels for 20 dollars per night. "
            "Tell us at least 3 days before the trip.",
    "date changes": "Hotel dates can be changed for free more than 14 days before the trip, "
                    "if the hotel has a room. A person confirms every change.",
}

WAITING_LIST = []  # Daniel's list: a person approves every refund and every change


def find_booking(booking_id):
    return BOOKINGS.get(booking_id, {"error": "booking not found"})


def get_refund_rules():
    return REFUND_RULES


def get_policy(topic):
    return POLICIES.get(topic, {"error": f"no policy for '{topic}'. Topics: {list(POLICIES)}"})


def prepare_refund(booking_id, amount, reason):
    item = {"type": "refund", "booking_id": booking_id, "amount": amount, "reason": reason,
            "status": "waiting for a person to approve"}
    WAITING_LIST.append(item)  # never sends money
    return item


def change_booking(booking_id, new_check_in, new_check_out):
    item = {"type": "change", "booking_id": booking_id, "new_check_in": new_check_in,
            "new_check_out": new_check_out, "status": "waiting for a person to confirm"}
    WAITING_LIST.append(item)  # never final without a person
    return item


def tool(name, description, properties):
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": properties, "required": list(properties)}}}


TEXT = {"type": "string"}
TOOLS = [
    tool("find_booking", "Look up a Nova Travel booking by its booking ID, like NT-4821.",
         {"booking_id": TEXT}),
    tool("get_refund_rules", "Read the Nova Travel refund rules.", {}),
    tool("get_policy", "Read a Nova Travel policy. Topics: pets, date changes.", {"topic": TEXT}),
    tool("prepare_refund", "Put a refund on the waiting list for a person to approve. "
         "It never sends money.",
         {"booking_id": TEXT, "amount": {"type": "number"}, "reason": TEXT}),
    tool("change_booking", "Put a hotel date change on the waiting list for a person to confirm.",
         {"booking_id": TEXT, "new_check_in": {"type": "string", "description": "Like June 13."},
          "new_check_out": {"type": "string", "description": "Like June 16."}}),
]
FUNCTIONS = {"find_booking": find_booking, "get_refund_rules": get_refund_rules,
             "get_policy": get_policy, "prepare_refund": prepare_refund,
             "change_booking": change_booking}

ANNA = (
    "Hi, this is Anna Weber. Sorry, a long message, we have a busy week. "
    "My husband cannot get time off work, so we cannot go to Barcelona, please cancel "
    "our family trip, booking NT-5602. "
    "Our Vienna hotel, NT-5603, should start one day later, so June 13 to June 16. "
    "Oh, and my mother Eva just called me. The airline cancelled her flight to Rome, "
    "her booking is NT-5604. What happens now? "
    "And one more question, can we bring our small dog to the Vienna hotel? "
    "Thank you so much!"
)
