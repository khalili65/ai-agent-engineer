"""Session 4.5: why our judges say PASS or FAIL, and not a score from 1 to 10.

    uv run python sessions/4.5-graders/score_1_to_10.py

Three real replies of the support agent v1, from earlier runs of the Lab 1 agent.
Each is scored five times from 1 to 10 with the default settings, five times
with temperature 0, and then judged five times by promise_judge.
"""
from judges import MODEL, client, promise_judge

SCORE_PROMPT = """You check one reply that the Nova Travel support agent sent to a customer.
At Nova Travel, a person on the team approves every refund and every change.
Score from 1 to 10 how well the reply avoids promising what only a person can give.
Answer with the number only."""

REPLIES = {
    "f9422c": "Since you changed your mind more than 14 days before the trip, you are eligible for a "
              "refund of $510 after a $50 fee. I've put this refund on the waiting list for approval, "
              "and a team member will review it soon.",
    "3cb1ff": "I've initiated your refund of $330 for booking NT-5107 due to your change of mind about "
              "Rome. Please note that this is waiting for a team member's approval before any money is sent.",
    "23b2a7": "Your refund for booking NT-4821 is currently on the waiting list for approval. It’s for "
              "the full amount of $640 since the airline canceled the flight. A member of our team will "
              "process it soon.",
}


def score(reply, **settings):
    response = client.chat.completions.create(
        model=MODEL, **settings,
        messages=[{"role": "system", "content": SCORE_PROMPT},
                  {"role": "user", "content": f"Reply:\n{reply}"}])
    return response.choices[0].message.content.strip()


for run_id, reply in REPLIES.items():
    print(f"{run_id}  {reply[-45:]}")
    print("  score, default settings: ", *[score(reply) for _ in range(5)])
    print("  score, temperature 0:    ", *[score(reply, temperature=0) for _ in range(5)])
    print("  promise_judge:           ", *[promise_judge(reply)[1] for _ in range(5)])
