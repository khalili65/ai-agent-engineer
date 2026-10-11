"""Session 3.3: async versions of the tools. The booking system is slow: about two seconds."""
import asyncio
from nova_tools import find_booking, get_refund_rules, prepare_refund

async def find_booking_slow(booking_id):
    await asyncio.sleep(2)  # the booking system needs two seconds; we wait without blocking
    return find_booking(booking_id)

async def get_refund_rules_async():
    return get_refund_rules()

async def prepare_refund_async(booking_id, amount, reason):
    return prepare_refund(booking_id, amount, reason)

# The same dispatch table idea, now with async functions
ASYNC_TOOL_FUNCTIONS = {
    "find_booking": find_booking_slow,
    "get_refund_rules": get_refund_rules_async,
    "prepare_refund": prepare_refund_async,
}

async def run_tool_async(name, args):
    function = ASYNC_TOOL_FUNCTIONS.get(name)
    if function is None:
        return {"error": f"unknown tool: {name}"}
    return await function(**args)
