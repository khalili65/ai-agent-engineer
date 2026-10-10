import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from tools import PENDING_REFUNDS, find_booking, prepare_refund  # noqa: E402


def test_find_booking():
    assert find_booking("NT-4821")["customer"] == "Sara"
    assert find_booking("NT-0000") == {"error": "booking not found"}


def test_refund_waits_for_a_person():
    refund = prepare_refund("NT-4821", 640.0, "airline cancelled the flight")
    assert refund["status"] == "waiting for approval"
    assert PENDING_REFUNDS[-1] == refund
