"""Session 3.4, version 1: tools made in a hurry, one tool per function of the booking system."""
from nova import raw_record, REFUND_RULES, WAITING_LIST

# 1. The functions
def get_data(id=None):
    return raw_record(id) or {"error": "not found"}

def get_booking_price(id=None):
    r = raw_record(id)
    return r["pricing"] if r else {"error": "not found"}

def get_booking_city(id=None):
    r = raw_record(id)
    return {"city": r["trip"]["destination_city"]} if r else {"error": "not found"}

def get_booking_dates(id=None):
    r = raw_record(id)
    return {"start": r["trip"]["start_date"], "end": r["trip"]["end_date"]} if r else {"error": "not found"}

def rules():
    return REFUND_RULES

def refund(id=None, amount=None, reason=None):
    WAITING_LIST.append({"booking_id": id, "amount": amount, "reason": reason,
                         "status": "waiting for a person to approve"})  # still no money moves
    return {"ok": True}

FUNCTIONS = {"get_data": get_data, "get_booking_price": get_booking_price,
             "get_booking_city": get_booking_city, "get_booking_dates": get_booking_dates,
             "rules": rules, "refund": refund}

# 2. What the model reads: vague names, no descriptions, every argument is loose text
def loose(name, *args):
    return {"type": "function", "function": {"name": name, "parameters": {
        "type": "object", "properties": {a: {"type": "string"} for a in args}}}}

TOOLS = [loose("get_data", "id"), loose("get_booking_price", "id"),
         loose("get_booking_city", "id"), loose("get_booking_dates", "id"),
         loose("rules"), loose("refund", "id", "amount", "reason")]
