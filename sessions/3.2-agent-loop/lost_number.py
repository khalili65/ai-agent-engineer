"""Session 3.2: Emma lost her booking number. The model starts to guess.

The loop stops after MAX_STEPS (6) model calls, and a person takes over.
"""
from agent_loop import run_agent
from nova_tools import EMMA

run_agent(EMMA)
