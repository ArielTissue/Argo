# Argo

### Knowledge-grounded, portfolio-aware investment analysis

Argo connects a reusable knowledge library, company evidence and a user's own portfolio
context to support deliberate investment decisions. It makes the reasoning before a
decision explicit: **why this company, why this valuation, why this position, and when
to reassess?**

[中文说明](README.zh-CN.md) · [Architecture](docs/architecture.md) · [Quick start](#quick-start) ·
[Connect your account](docs/account-connection.md) · [Evaluation](docs/evaluation.md)

![Argo framework](docs/assets/framework.svg)

## The framework

Argo is organized by responsibilities, rather than simulated trading-team roles:

| Module | Responsibility |
|---|---|
| **Context** | Source-backed knowledge, confirmed user policy, prior research and unresolved questions |
| **Research** | Verify an earnings release, collect official disclosures, preserve periods and source locations |
| **Analysis** | Apply valuation assumptions, business-quality reasoning and a bear case |
| **Portfolio context** | Read a user-authorized account snapshot; preserve role, theme, cash-purpose and timestamp distinctions |
| **Skills** | Teach an existing agent host how to combine the context and tools |
| **Harness** | Prepare a task, compute policy context, validate a proposal, stage a preview and control archival writes |
| **Human decision** | Review the assumptions, purpose of the position and conditions for exit or reassessment |

Two users can receive different action suggestions from the same company analysis
because their existing exposure, available funds and policies differ. A favorable
valuation scenario alone does not resolve a portfolio constraint.

## Current scope — v0.1 foundation

**Implemented:** installable Python CLI, editable watchlist, release-aware task planning,
portfolio context computation, knowledge selection, structured proposal validation,
three-attempt validation budget, staged reports, explicit apply, concurrency checks,
run traces, a broker-tool allowlist, a host-agent skill and synthetic replay.

**Requires an agent host:** live web research, LLM analysis and existing IBKR plugin
calls. The bundled skill guides these tasks; the Python package does not authenticate
to a hosted plugin or run its own LLM loop. The `HostBroker` seam is tested with a fake
transport. A live IBKR transport has **not** been integration-tested in this release.

**Not implemented:** automatic calendar-provider integration, background scheduling,
automated knowledge ingestion/linting, automatic ETF look-through, strategy backtesting
or order execution. Calendar refresh and scheduling are delegated to the user's host.
The architecture describes how these responsibilities fit together, not a claim that
all modules run unattended.

## Quick start

Python **3.11+**. No third-party runtime dependencies are required by the core.

```bash
# After cloning this repository:
python3 -m venv .venv
source .venv/bin/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
argo demo --output ./demo-output
```

The demo uses **fictional companies, a fixed clock and a fixture response**. No model,
network, brokerage account or API key is used. The output reports are labeled
`fixture-replay`; this demonstrates the harness, not live reasoning quality.

Look at:

```text
demo-output/
├── watchlist.json, policy.json, portfolio.json, earnings.json
├── knowledge/                 # new, synthetic teaching notes
├── runs/<id>/
│   ├── context.md, task.json  # selected inputs and their hashes
│   ├── proposal.json          # fixture or host-produced response
│   ├── report.md              # inspectable preview
│   ├── changes.json           # exact proposed writes
│   └── trace.jsonl            # execution events, not hidden model reasoning
├── outputs/research/AURX/AURX-FY2026-Q3.md
├── outputs/calendar.md        # one short index row per reviewed release
└── receipts/                  # applied event IDs and output hashes
```

In the example, the assumed valuation implies a 33.33% margin of safety, but the
portfolio violates its stock/theme limits and technology additions are frozen.
The result is **wait**. An estimated after-market event is not analyzed before release.

## Bring your own watchlist

Create a separate private workspace:

```bash
argo init ~/argo-workspace
argo watchlist ~/argo-workspace --add MSFT --company Microsoft \
  --ir-url https://www.microsoft.com/en-us/Investor
argo watchlist ~/argo-workspace --remove AURX
argo watchlist ~/argo-workspace --remove HARB
argo plan ~/argo-workspace
```

`init` writes **example** policy, portfolio and calendar files. Replace them with your
own reviewed data before live work. If no portfolio is available, remove
`portfolio.json`; Argo treats it as unknown, not zero holdings. Newly added symbols
show `date_unknown` until a calendar source is supplied.

The agent host checks official IR announcements and populates the earnings contract;
Argo does not infer an earnings date from a fiscal quarter end or an SEC filing deadline.
Update the verified data through:

```bash
argo import-data ~/argo-workspace --kind calendar --file ./verified-calendar.json
argo import-data ~/argo-workspace --kind portfolio --file ./normalized-snapshot.json
```

See [data contracts](docs/data-contracts.md) for complete fields, units, dates and rule IDs.

## Run with your agent host

A local plugin is included at `plugins/argo/`. Its skill guides an authenticated agent
through official-source research and the harness. The host supplies the model, web tools
and any user-installed brokerage plugin; Argo supplies the task and acceptance contract.

For supported Codex desktop local-plugin workflows:

```bash
codex plugin marketplace add .
```

Install **Argo** from the `argo-local` source in the desktop Plugins Directory, then
start a fresh session. Availability varies by host. No global settings are modified by
`pip install .`. See [installation](docs/installation.md).

Example request:

> Use Argo to check my watchlist in ~/argo-workspace, verify releases from official
> sources, use my connected IBKR account as read-only context if available, and stage
> a source-backed analysis. Show me the proposed changes before applying them.

The skill uses:

```bash
argo prepare ~/argo-workspace --symbol MSFT
# The host reads runs/<id>/context.md, retrieves evidence, and writes a proposal.
argo stage ~/argo-workspace --run <id> --proposal ./proposal.json
# Inspect the staged report and changes. The user explicitly runs:
argo apply ~/argo-workspace --run <id>
```

A third failed proposal ends the repair budget for that task. Editing the policy,
portfolio, calendar, selected knowledge or output files after preparation invalidates
the task; prepare a new one rather than silently mixing versions.

## Account connection and privacy

Use your **own** installed/authenticated plugin. Downloading Argo does not inherit the
author's session or account access. Argo never requests brokerage passwords or stores
them. The Python `HostBroker` wrapper allows only account/price read operations; a host
that exposes additional tools must configure its own permissions. A prompt prohibition
alone does not remove a tool's authority.

Keep personal workspaces outside the repository. The demo data and policy are newly
authored fixtures, not anonymized personal accounts. This release has no transaction
execution path. See [account connection](docs/account-connection.md).

## Evaluation and limitations

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Tests cover release timing, missing context, the same company with different portfolios,
policy gates, evidence/reference structure, stale inputs, bounded repair, unauthorized
paths, concurrent edits and duplicate application. These are **software behavior tests**,
not LLM accuracy, valuation validity or investment-return results.

The source validator checks references, declared source type and timestamps. It does
not authenticate a source or prove that an excerpt supports a claim. Review original
disclosures. An intrinsic value is an assumption, even when its arithmetic is correct.
Source documents should be treated as untrusted data by the agent host.

## Design notes and roadmap

- [Architecture and trust model](docs/architecture.md)
- [Data contracts](docs/data-contracts.md)
- [Host/plugin connection](docs/account-connection.md)
- [Evaluation plan and observed checks](docs/evaluation.md)
- [Roadmap](docs/roadmap.md)

The presentation of [TradingAgents](https://github.com/TauricResearch/TradingAgents)
inspired the framework-first repository structure. Argo is an independent implementation;
no TradingAgents code is bundled. The wiki-centered knowledge organization was inspired
by [Andrej Karpathy's LLM Wiki idea](https://lnkd.in/g2vFrXM2).

Research and learning software. Outputs are uncertain decision support, not an assurance
of investment performance or an instruction to transact.

## License

[MIT](LICENSE). Third-party data accessed by a user remains subject to its source terms.
