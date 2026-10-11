"""Session 3.4: the Nova Travel booking system (a local stand-in) and Daniel's waiting list."""
import json
from pathlib import Path

# The booking system returns big raw records, like a real company system does
SYSTEM_RECORDS = json.loads((Path(__file__).parent / "booking_system.json").read_text())

REFUND_RULES = [
    "If the airline cancels the flight, the customer gets a full refund.",
    "If the customer changes their mind more than 14 days before the trip, "
    "they get the price minus a 50 dollar fee.",
    "If the customer changes their mind 14 days or less before the trip, there is no refund.",
]

WAITING_LIST = []  # Daniel's list: a person approves every refund, no money moves here


def raw_record(booking_id):
    """Everything the booking system knows: about 1,000 tokens per booking."""
    return SYSTEM_RECORDS.get(booking_id)


def short_record(booking_id):
    """Only what the support agent needs, in plain words."""
    r = SYSTEM_RECORDS.get(booking_id)
    if r is None:
        return None
    trip = r["trip"]
    flights = [s for s in r["segments"] if s["type"] == "flight"]
    if not flights:
        flight = "no flight in this booking"
    elif all(s["status_code"] == "XX" for s in flights):
        flight = "cancelled by the airline"
    else:
        flight = "on time"
    return {
        "booking_id": booking_id,
        "customer": r["customer"]["first_name"],
        "trip": f'{trip["destination_city"]}, {trip["nights"]} nights, '
                + ("flight + hotel" if trip["product"] == "FLIGHT_HOTEL" else "hotel only"),
        "dates": f'{trip["start_date"]} to {trip["end_date"]}',
        "days_before_trip": trip["days_to_departure"],
        "price_paid": r["pricing"]["total_paid_cents"] / 100,
        "flight": flight,
    }
