"""Session 3.2: a token budget. We allow up to 20 steps, but only 3,000 tokens for one message.

Every step sends the whole conversation again, so every step costs a little more.
"""
from agent_loop import run_agent
from nova_tools import EMMA

run_agent(EMMA, max_steps=20, max_tokens=3_000)
