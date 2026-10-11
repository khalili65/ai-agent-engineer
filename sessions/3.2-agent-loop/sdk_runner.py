"""Session 3.2: the same support agent with a tool runner from the OpenAI Agents SDK.

Runner.run_sync runs the whole loop for us: call the model, run the tools,
add the results, and stop on a final answer or after max_turns.
"""
import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, MaxTurnsExceeded
import nova_tools
from nova_tools import SYSTEM, SARA, EMMA, WAITING_LIST

load_dotenv()
MODEL = os.getenv("MODEL", "gpt-4o-mini")


@function_tool
def find_booking(booking_id: str) -> dict:
    """Look up a Nova Travel booking by its booking ID, like NT-4821."""
    return nova_tools.find_booking(booking_id)


@function_tool
def get_refund_rules() -> dict:
    """Get the Nova Travel refund rules."""
    return nova_tools.get_refund_rules()


@function_tool
def prepare_refund(booking_id: str, amount: float, reason: str) -> dict:
    """Prepare a refund request. It does not send money: it puts the request on the list for a person to approve."""
    return nova_tools.prepare_refund(booking_id, amount, reason)


agent = Agent(name="Nova support agent", instructions=SYSTEM, model=MODEL,
              tools=[find_booking, get_refund_rules, prepare_refund])

for message in [SARA, EMMA]:
    print("Customer:", message[:40] + "...")
    try:
        result = Runner.run_sync(agent, message, max_turns=6)
        usage = result.context_wrapper.usage
        print("Agent:", result.final_output)
        print(f"Model calls: {usage.requests}, tokens: {usage.input_tokens} input + "
              f"{usage.output_tokens} output")
    except MaxTurnsExceeded as error:
        print(f"STOP: {error}. A person takes over.")
    print()

print("Waiting list:", WAITING_LIST)
