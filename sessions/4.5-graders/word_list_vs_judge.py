"""Session 4.5: the rough word check from session 4.4 next to the promise judge.

    uv run python sessions/4.5-graders/word_list_vs_judge.py

Two test replies that we wrote ourselves. Both make a promise, with words that are not on the list.
"""
from judges import promise_judge

PROMISE_WORDS = ["soon", "shortly", "will be approved", "i will notify"]  # the list from session 4.4

TEST_REPLIES = [
    "Good news! Your 330 dollars are on their way to your card.",
    "Your refund is on the waiting list, and Daniel will approve it tomorrow morning.",
]

for reply in TEST_REPLIES:
    found = [w for w in PROMISE_WORDS if w in reply.lower()]
    reason, verdict = promise_judge(reply)
    print(reply)
    print(f"  word check:    {'FAIL ' + str(found) if found else 'PASS'}")
    print(f"  promise_judge: {verdict}  ({reason})\n")
