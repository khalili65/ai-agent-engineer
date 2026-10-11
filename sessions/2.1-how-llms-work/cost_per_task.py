"""Session 2.1: the same task on several models. It measures the tokens and the cost of one task."""
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# Dollars per 1 million tokens: (input, output).
# From https://developers.openai.com/api/docs/pricing. Prices change often: check the page again.
PRICES = {
    "gpt-6-astra": (10.00, 50.00),   # premium
    "gpt-6.1-sol": (2.00, 10.00),    # workhorse
    "gpt-6-luna":  (0.10, 0.50),     # small
    "gpt-4o-mini": (0.15, 0.60),     # the model our support agent uses today
}
RUNS = 3                   # token counts change a little from run to run, so we take the average
TASKS_PER_MONTH = 9_000    # Daniel's estimate: about 300 customer messages a day

# The task: write the support agent's answer to Sara, using the booking facts and the rules.
INSTRUCTIONS = (
    "You are the Nova Travel support agent. Refund rules: if the airline cancels a flight, "
    "the customer gets a full refund. You never send refunds yourself; a person approves "
    "every refund. Answer in two or three short sentences.\n"
    "Booking NT-4821: Sara, Lisbon, 5 nights, flight + hotel, $640.00, "
    "flight cancelled by the airline."
)
SARA = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
        "My booking is NT-4821. Can I get my money back?")

def run_task(model):
    """Answer Sara once. Return the answer, input tokens, output tokens, thinking tokens."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": INSTRUCTIONS},
                  {"role": "user", "content": SARA}],
    )
    usage = response.usage
    details = usage.completion_tokens_details
    thinking = (details.reasoning_tokens or 0) if details else 0  # hidden, but paid as output
    return response.choices[0].message.content, usage.prompt_tokens, usage.completion_tokens, thinking

table = []
for model in sys.argv[1:] or PRICES:
    price_in, price_out = PRICES.get(model, (0.0, 0.0))   # a model not in the list counts as free
    costs = []
    print(f"{model}  (${price_in:.2f} input, ${price_out:.2f} output per 1M tokens)")
    for run in range(1, RUNS + 1):
        answer, inp, out, thinking = run_task(model)
        cost = inp / 1_000_000 * price_in + out / 1_000_000 * price_out
        costs.append(cost)
        print(f"  run {run}: input {inp} + output {out} (thinking {thinking}) tokens = ${cost:.6f}")
    print(f"  answer: {answer}\n")
    table.append((model, sum(costs) / RUNS))

print(f"{'model':<13}{'cost per task':>15}{'per month':>12}   ({TASKS_PER_MONTH:,} tasks)")
for model, avg in table:
    print(f"{model:<13}{'$' + format(avg, '.6f'):>15}{'$' + format(avg * TASKS_PER_MONTH, '.2f'):>12}")
