# Failure taxonomy of the support agent v1

Made by reading 40 real traces by hand (one working day, `messages.jsonl` → `traces/traces.jsonl`).
Every trace has one note and, if it failed, one category in `labels.jsonl`.

**Result:** 40 traces read · 20 passed · 20 failed · 5 more were wrong at one step but caught by a tool.
The last new category appeared at trace 21. Traces 22 to 40 added no new category (saturation).

| # | Category (key) | Count | Traces | Where it shows in the trace | Grader that can catch it (Section 4) |
|---|---|---|---|---|---|
| 1 | `guesses_beyond_tools` | 8 | 15, 25, 28, 29, 30, 33, 34, 39 | the final reply (or a tool used for something it was not made for) | `facts_judge`; human review |
| 2 | `blind_to_waiting_list` | 6 | 8, 17, 31, 32, 36, 40 | a `prepare_refund` call for a refund that is already waiting, or a final reply about a refund status | code check: one refund per booking on the waiting list |
| 3 | `promises_for_a_person` | 3 | 5, 12, 19 | the final reply | `promise_judge` |
| 4 | `rules_said_wrong` | 2 | 13, 14 | the final reply | `facts_judge` |
| 5 | `shares_booking_with_stranger` | 1 | 21 | the final reply | code check or human review |

## 1. `guesses_beyond_tools` — answers a question that no tool or rule covers, by guessing (8 of 40)
The customer asks something our tools and policy do not cover (pets, insurance, vouchers, an overweight bag,
a double charge, an upgrade, one night less). The agent does not say "I don't know, a person will check".
It makes up an answer.
- 15 (`7db6aa`): "You can bring a small dog on your Barcelona flight…" The policy says nothing about pets.
- 29 (`5b8d3d`): "Your Lisbon booking NT-4821 does not include travel insurance." The booking has no insurance field.
- 39 (`93618b`): "…there is no duplicate charge." The booking has no payment data.
- 33 (`007661`): `prepare_change` with `"change": "upgrade to a room with a sea view", "fee": 0`, then "there is no fee for this change". The changes policy is about dates.
- 28 (`63cfb6`): no tool call at all; "5 to 10 business days… depending on your bank's processing times". The number is right by luck.
- **First upstream failure:** the step where the agent decides to answer (or to use `prepare_change`) instead of handing over to a person. Root cause: the agent has no "hand over to a person" path, and the instructions do not say what to do when no rule covers a question.

## 2. `blind_to_waiting_list` — a follow-up about an existing refund (6 of 40)
The customer asks about a refund that is already waiting ("did my refund go through?", "when will the money
arrive?", "please cancel the refund"). No tool can read the waiting list, so the agent either prepares the
same refund again or says something wrong about it.
- 8 (`95ce46`), 17 (`e5ddbb`), 31 (`cceb58`), 36 (`1444b3`): a second (or third) refund for the same booking.
  At the end of the day Daniel's list holds NT-4821 × 3 (640 each), NT-5107 × 2 (330), NT-7120 × 2 (830).
- 32 (`a0bc4c`): "Your booking NT-6631 has not been refunded yet. Would you like me to prepare a refund for you?" — 470 has been waiting since trace 7.
- 40 (`6e9656`): "…there's no need for a refund since you've decided to go." — the 470 refund is still on the list.
- **First upstream failure:** step 8 `prepare_refund` (traces 8, 17, 31, 36) — the reply after it only repeats it.
  The deeper cause sits before step 1: the tool set has no way to look at the waiting list. One fix (a tool that reads the list, or a code check in `prepare_refund`) covers all six traces.

## 3. `promises_for_a_person` — promises an approval or a time that only a person can give (3 of 40)
- 5 (`3f3ec4`) and 19 (`52e1ee`): "A member of our team will confirm the change shortly."
- 12 (`8559fc`): "…it will be reviewed and approved by our team before processing."
- Every tool step is right; only the final reply is wrong. (Trace 17 also says "I will notify you", but its first failure is the second refund, so it counts as category 2.)

## 4. `rules_said_wrong` — the reply states the refund rules wrong (2 of 40)
- 13 (`ea76c5`): "Refunds are only applicable when an airline cancels a flight."
- 14 (`8dbeac`): "…refunds are only available if the airline cancels the flight."
- The rules also give a changed-mind refund more than 14 days before the trip. The decision (no refund) was right both times; the sentence about the rules was not.

## 5. `shares_booking_with_stranger` — tells someone about another customer's booking (1 of 40)
- 21 (`9bc344`): "Mike" asks about NT-4821 (Sara's booking) and gets its status and price. Nothing checks who is asking.

## Caught by a tool (not a failure for the customer, but worth knowing)
In 5 traces one step was wrong, and the rules written as code in `prepare_refund` refused it:
4 (670 for Lukas), 6 (400 for Olivia at exactly 14 days), 18 (240 for Maria's Porto trip),
14 and 22 (720 with reason `airline_cancelled`, because the customer said so). The final replies were right.
Without the check in `refund_amount`, these would be five wrong refunds on Daniel's list.

## How this was made
1. **Collect:** `collect_traces.py` sent 40 messages (refunds, changes, bags, follow-ups, typos, edge days, angry customers, one in Spanish) to the v1 agent, in one process, like one day.
2. **Open coding:** read every trace with `show_trace.py` and wrote one short free note per trace, without categories.
3. **Axial coding:** grouped the notes of the failed traces into categories, then gave each failed trace one category: the category of its **first** failure.
4. **Count and saturation:** `count_labels.py` counts the categories and shows the trace where each one first appeared.
Every note and label was written by hand while reading the trace. No model was asked to label.
