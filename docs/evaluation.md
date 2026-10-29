# Evaluation

## What has been implemented

The standard-library test suite runs the public workflow interface against fresh
synthetic workspaces. It exercises release timing, missing dates, stale/changed context,
portfolio-aware addition gates, reserved cash arithmetic, evidence-reference checks,
knowledge links, bounded failures, write targets, concurrent edits and idempotence.
Run it with `python -m unittest discover -s tests -v`.

`argo demo` replays a fixture proposal through the actual harness. It is not a live LLM
run, and its sources are explicit example.org placeholders. Tests and the fixture prove
specified software behavior, not accuracy of generated financial analysis.

## Live agent evaluation to add

Use a fixed, dated set of original disclosures and a manually verified answer set.
Separate:

| Layer | Observable evaluation |
|---|---|
| Fact extraction | Correct figure, reporting period, unit, currency and source location |
| Arithmetic | Independently recomputed numbers with fixed inputs |
| Research | Unsupported claims, unresolved questions, source coverage |
| Analysis | Explicit assumptions, bear case, scenario sensitivity, evidence consistency |
| Personalization | Same company, different synthetic portfolios; appropriate constraint changes |
| Execution | No premature release analysis, repeated-run behavior, restricted write targets |

Record sample sizes and failure categories. A validator acceptance rate is not factual
accuracy, and a matching source ID is not proof that the source supports the claim.
Never use information published after the task's as-of time in a historical replay.

## Decision-process value

Users can record position purpose, reasons and exit/reassessment conditions. A claim
that the system changed behavior needs original decision records and comparison evidence.
A retrospective `wait` label does not prove a real trade was prevented. Merely touching
a later price band does not show that waiting was a good investment decision.

No investment-return backtest or behavioral-improvement result is claimed here.
