"""Session 2.1: watch the model choose its next token, with the top candidates and their chances."""
import math
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")

SENTENCES = [
    "The airline cancelled Sara's flight, so Nova Travel will give her a full",
    "After Lisbon, Sara wants a short holiday in May. Nova Travel suggests a trip to",
]

for sentence in SENTENCES:
    reply = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": f"Finish this sentence with one word: {sentence}"}],
        max_tokens=1,       # we only want the next token
        logprobs=True,      # return how likely each token was
        top_logprobs=5,     # and the 5 best candidates
    )
    print(f"{sentence} ...")
    for c in reply.choices[0].logprobs.content[0].top_logprobs:
        print(f"  {c.token!r:12} {math.exp(c.logprob):7.2%}")   # logprob -> probability
    print(f"  It wrote: {reply.choices[0].message.content!r}\n")
