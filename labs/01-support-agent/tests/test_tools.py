"""Quick tests for the tools. They need no model and no key, and they cost nothing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from tools import WAITING, WAITING_LIST, find_booking, get_policy, prepare_change, prepare_refund  # noqa: E402


def test_find_booking():
    assert find_booking("NT-4821")["customer"] == "Sara"


def test_unknown_booking_gives_a_hint():
    result = find_booking("NT-739")
    assert "error" in result and "hint" in result


def test_policy_topic():
    assert "8 kg" in get_policy("baggage")["policy"]
    assert "hint" in get_policy("pets")


def test_refund_only_waits_for_a_person():
    refund = prepare_refund("NT-4821", 640.0, "airline_cancelled")
    assert refund["status"] == WAITING
    assert WAITING_LIST[-1] == refund


def test_refund_follows_the_rules():
    assert prepare_refund("NT-5107", 330.0, "changed_mind")["amount"] == 330.0   # John, 30 days
    assert "error" in prepare_refund("NT-6190", 670.0, "changed_mind")          # Lukas, 10 days
    assert "error" in prepare_refund("NT-4821", 6400.0, "airline_cancelled")    # wrong amount


def test_change_fee_follows_the_policy():
    assert prepare_change("NT-5307", "two days later", 30.0)["status"] == WAITING  # Tom, 1 day
    assert "error" in prepare_change("NT-5307", "two days later", 100.0)
