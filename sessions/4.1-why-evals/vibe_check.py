"""A vibe check: send each message once and read the replies. Nothing else.

    uv run python sessions/4.1-why-evals/vibe_check.py
"""
from tasks import TASKS, run_task

for task in TASKS:
    reply, trace, waiting = run_task(task)
    print(f"Customer: {task['message']}")
    print(f"Agent:    {reply}\n")
