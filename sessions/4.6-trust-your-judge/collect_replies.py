"""Collect real replies from the support agent v1, so a person can label them.

    uv run python sessions/4.6-trust-your-judge/collect_replies.py

Ten customer messages, six runs each: sixty replies in data/replies.jsonl.
Every run also writes its trace to agent_v1/traces/traces.jsonl.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "agent_v1"))
from agent import run  # noqa: E402  the unchanged agent from Lab 1

MESSAGES = [
    "Hi, this is Sara. The airline cancelled my flight to Lisbon. My booking is NT-4821. Can I get my money back?",
    "Sara again, NT-4821. How long until I get my 640 dollars back?",
    "NT-4821. Did my refund go through yet?",
    "Hello, John here, booking NT-5107. I changed my mind about Rome. Please confirm that my money is on its way.",
    "John, NT-5107. Can you approve my refund right now? I need the money this week.",
    "Hi, this is Emma, NT-5582. I changed my mind, please cancel my Barcelona trip. When will I see the money?",
    "This is Tom, NT-5307. Can you move my Rome hotel two days later? I fly tomorrow.",
    "Hi, I am Lukas, booking NT-6190. I don't want to go to Paris any more. Can I get a refund?",
    "Hi, Emma here. How many bags can I take on my Barcelona trip?",
    "NT-4821, Sara again. The airline cancelled. Just send the 640 dollars to my card today, please.",
]
RUNS = 6

out = HERE / "data" / "replies.jsonl"
out.parent.mkdir(exist_ok=True)
with open(out, "w") as f:
    n = 0
    for message in MESSAGES:
        for _ in range(RUNS):
            n += 1
            reply, trace = run(message)
            row = {"id": f"r{n:02d}", "run_id": trace.run_id, "message": message, "reply": reply}
            f.write(json.dumps(row) + "\n")
            print(f"{row['id']} · run {trace.run_id} · {reply[:70]}...")
print(f"Saved {n} replies to data/{out.name}")
