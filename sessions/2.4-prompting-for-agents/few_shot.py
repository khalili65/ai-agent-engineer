"""Session 2.4: few-shot. We add one example answer to the system prompt."""
from altitude import RIGHT
from support_agent import run_agent

EXAMPLE = """
Here is an example of a good answer. Always use the same shape.

<example>
Customer: Hi, I changed my mind about my trip to Rome. My booking is NT-3307. Can I get a refund?
Agent:
Hi Tom,
Booking: NT-3307 · Rome · 3 nights · $410.00
What the rules say: you changed your mind 30 days before the trip, so you get a refund minus a fee.
Next step: a person on our team checks this today and confirms the refund by email.
Nova Travel Support
</example>"""

print("=== WITHOUT AN EXAMPLE ===")
print("Agent:", run_agent(RIGHT))
print()
print("=== WITH ONE EXAMPLE ===")
print("Agent:", run_agent(RIGHT + "\n" + EXAMPLE))
