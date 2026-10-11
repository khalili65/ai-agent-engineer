"""The support agent v1 from Lab 1, used exactly as it is.

Only two things change: the agent also knows the new bookings in data/bookings.json,
and it writes its traces into this folder (traces/traces.jsonl).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
LAB1 = HERE.parent.parent / "labs" / "01-support-agent"
sys.dont_write_bytecode = True
sys.path.insert(0, str(LAB1))

import tools  # noqa: E402
import trace_log  # noqa: E402

trace_log.TRACE_DIR = HERE / "traces"
tools.BOOKINGS.update(json.loads((HERE / "data" / "bookings.json").read_text()))

from agent import run  # noqa: E402,F401
from tools import BOOKINGS, WAITING, WAITING_LIST, change_fee, refund_amount  # noqa: E402,F401
