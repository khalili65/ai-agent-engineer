"""Session 3.4: version one, then one fix at a time (each step keeps the fixes before it).

step1  fix 1: the booking input is called booking_id, with a description and a pattern
step2  fix 2: one tool, find_booking, sends back what the agent needs, in plain words
step3  fix 3: an honest refund tool: prepare_refund says what really happens
"""
import tools_v1
import tools_v2


def tool(name, properties):
    return {"type": "function", "function": {"name": name, "parameters": {
        "type": "object", "properties": properties}}}


# Fix 1: a clear name and a description for the booking input
BOOKING_ID = {"type": "string", "pattern": "^NT-[0-9]{4}$",
              "description": "The booking ID in capitals, like NT-4821. "
                             "If the customer writes nt 4821 or 4821, use NT-4821."}

def with_booking_id(function):
    return lambda booking_id=None, **rest: function(id=booking_id, **rest)

STEP1_FUNCTIONS = {name: function if name == "rules" else with_booking_id(function)
                   for name, function in tools_v1.FUNCTIONS.items()}
STEP1_TOOLS = [tool(name, {"booking_id": BOOKING_ID}) for name in
               ("get_data", "get_booking_price", "get_booking_city", "get_booking_dates")] + [
              tool("rules", {}),
              tool("refund", {"booking_id": BOOKING_ID, "amount": {"type": "string"},
                              "reason": {"type": "string"}})]

# Fix 2: one find_booking tool instead of four, and it sends back what the agent needs
STEP2_FUNCTIONS = {"find_booking": tools_v2.find_booking, "rules": tools_v1.rules,
                   "refund": STEP1_FUNCTIONS["refund"]}
STEP2_TOOLS = [tools_v2.TOOLS[0], STEP1_TOOLS[4], STEP1_TOOLS[5]]

# Fix 3: the refund tool gets an honest name and description, and it answers with the request
STEP3_FUNCTIONS = {"find_booking": tools_v2.find_booking, "rules": tools_v1.rules,
                   "prepare_refund": tools_v2.prepare_refund}
STEP3_TOOLS = [tools_v2.TOOLS[0], STEP1_TOOLS[4], tools_v2.TOOLS[2]]
