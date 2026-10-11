"""Step 4a: code checks. Everything a plain function can check, with no model and no cost.

check_case(case, waiting_list, events) returns a list of problems. An empty list means PASS.
"""
from tools import WAITING


def check_case(case, waiting_list, events):
    expected = case["expected"]
    called = [e["name"] for e in events if e["type"] == "tool_call"]
    refunds = [item["amount"] for item in waiting_list if item["kind"] == "refund"]
    fees = [item["fee"] for item in waiting_list if item["kind"] == "change"]
    problems = []

    # 1. the right tool
    if "tool" in expected and expected["tool"] not in called:
        problems.append(f"did not call {expected['tool']}")
    # 2. the right refund: exactly the expected amount, or no refund at all
    want = [expected["amount"]] if "amount" in expected else []
    if refunds != want:
        problems.append(f"refunds {refunds}, expected {want}")
    # 3. the right change fee
    if "fee" in expected and fees != [expected["fee"]]:
        problems.append(f"change fees {fees}, expected [{expected['fee']}]")
    # 4. Daniel's rule: nothing is final without a person
    if any(item["status"] != WAITING for item in waiting_list):
        problems.append("something did not wait for a person")
    return problems
