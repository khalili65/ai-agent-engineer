# Session 4.6: Trust your judge

The promise judge reads one reply of the support agent and says PASS or FAIL:
does the reply promise an approval, a payment or a time that only a person can give?
But a judge is also a model, and it makes mistakes. So before Daniel trusts its numbers,
we compare it with a person: Daniel labels sixty real replies, and we measure how often the judge agrees.

| File | What it does |
|---|---|
| `agent_v1/` | An unchanged copy of the support agent v1 from Lab 1 (it writes its traces to `agent_v1/traces/`). |
| `collect_replies.py` | Sends ten customer messages to the agent, six times each: sixty real replies in `data/replies.jsonl`. |
| `label.py` | A tiny labeling tool: a person reads each reply and types PASS or FAIL and a short note (`data/labels.jsonl`). |
| `split.py` | Splits the labels into `train` (20%), `dev` (40%) and `test` (40%), with the same share of FAIL labels in each. |
| `promise_judge.py` | The judge prompts: `v1` (the question only), `v2` (Daniel's rules and three examples from train), `v3` (tried on dev, not kept). |
| `measure.py` | Runs a judge version on a group and prints every disagreement, the TPR and the TNR. |
| `position_bias.py` | A pairwise judge picks the better of two replies, once in each order, and we count how often the order decided. |

```bash
uv run python sessions/4.6-trust-your-judge/collect_replies.py   # about 2 cents
uv run python sessions/4.6-trust-your-judge/label.py             # you type p or f, and a note
uv run python sessions/4.6-trust-your-judge/split.py
uv run python sessions/4.6-trust-your-judge/measure.py v1 dev
uv run python sessions/4.6-trust-your-judge/measure.py v2 dev
uv run python sessions/4.6-trust-your-judge/measure.py v2 test    # only once, at the very end
uv run python sessions/4.6-trust-your-judge/position_bias.py
```

The `data/` folder already holds the replies and the labels from the video, so you can start at `split.py`.
Every judge run costs well under one cent with `gpt-4o-mini`.

## Two numbers

A failure is what the judge must find, so a FAIL is called a *positive*.

- **TPR, the true positive rate:** of the replies the person marked FAIL, how many the judge also marked FAIL.
- **TNR, the true negative rate:** of the replies the person marked PASS, how many the judge also marked PASS.

Look at both. The first prompt agreed with Daniel on 19 of 24 dev replies, but it caught 0 of the 4 failures.

## Results from the video (gpt-4o-mini, temperature 0)

| Judge | Group | TPR | TNR |
|---|---|---|---|
| v1 | dev | 0/4 | 19/20 |
| v2 | dev | 3/4 | 17/20 |
| v3 | dev | 4/4 | 15/20 |
| v2 | test (once) | 5/5 | 17/19 |

Position bias: in 11 of 30 pairs, the pairwise judge picked the same place both times (9 times the second reply, 2 times the first).
The fix: ask in both orders, and count a pair only when both answers pick the same reply; otherwise it is a tie.

Your runs will differ a little: models are not fully repeatable, even at temperature 0.
