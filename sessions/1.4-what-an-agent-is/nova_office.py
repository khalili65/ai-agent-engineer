"""Session 1.4: the plain Python part of Nova Travel. No AI in this file."""

# A small stand-in for the company booking system
BOOKINGS = {
    "NT-4821": {"customer": "Sara", "trip": "Lisbon, 5 nights, flight + hotel", "price": 640.00,
                "flight": "cancelled by the airline", "days_before_trip": 9},
    "NT-5107": {"customer": "Omar", "trip": "Rome, 3 nights, hotel only", "price": 380.00,
                "flight": "none", "days_before_trip": 30},
}

WAITING_FOR_APPROVAL = []  # refunds that wait for a person (Daniel's rule)


def find_booking(booking_id):
    return BOOKINGS.get(booking_id, {"error": "booking not found"})


def prepare_refund(booking_id, amount):
    """Prepare a refund. It never sends money: a person must approve it first."""
    refund = {"booking_id": booking_id, "amount": amount, "status": "waiting for a person to approve"}
    WAITING_FOR_APPROVAL.append(refund)
    return refund
