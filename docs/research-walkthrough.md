# Use Argo for a company earnings analysis

The main task is to explain business quality, cash economics, valuation uncertainty
and what to investigate next. Portfolio context adds a second question: does the
idea fit this user's constraints? It is optional for research; an absent portfolio
is unknown, and blocks an affirmative addition stance rather than blocking analysis.

## 1. Inspect a complete offline report

After installing the Python package, run:

```bash
argo demo --output ./earnings-demo
```

Open `earnings-demo/outputs/research/AURX/AURX-FY2026-Q3.md`.
A [checked-in copy](examples/aurx-earnings-report.md) can be read without installing.
All company figures, sources, valuation inputs and portfolio values in this example
are fictional. The command replays a supplied response; it does not call a model.
The response lives in `examples/proposal.json`, so readers can inspect evidence links,
claims, assumptions and the resulting report together.

## 2. Prepare a private live workspace

```bash
argo init ~/argo-research
argo watchlist ~/argo-research --add MSFT --company Microsoft \
  --ir-url https://www.microsoft.com/en-us/Investor
argo watchlist ~/argo-research --remove AURX
argo watchlist ~/argo-research --remove HARB
```

Replace the demo policy with the user's reviewed policy. Replace the synthetic
portfolio with a current snapshot, or remove `~/argo-research/portfolio.json` for
company research without personal holdings. Never present the bundled portfolio as
a real account. Review the knowledge framework and adapt it explicitly if desired.

## 3. Ask your agent host to perform the research

Install the optional [host skill/plugin](installation.md#optional-local-host-plugin),
or provide `plugins/argo/skills/argo-research/SKILL.md` as instructions in a host
that can read local files, run the CLI and access official disclosures. Python
installation alone does not register a skill or supply an LLM/web service.
An example request to the host is:

> Use Argo in ~/argo-research to analyze Microsoft's latest verified released
> earnings. Verify the reporting period and source directly from official IR or
> filings. Use the default investment framework, explain revenue/margin changes,
> reconcile FCF and SBC, test the moat and bear case, and show explicit valuation
> scenarios with their limitations. I have no portfolio snapshot for this run:
> keep company research separate from personal suitability. Prepare and stage
> a report for my review; do not archive it or execute any trade.

The host verifies the event and writes a calendar import matching
[the data contract](data-contracts.md). Then it runs:

```bash
argo import-data ~/argo-research --kind calendar --file /path/to/verified-calendar.json
argo plan ~/argo-research
argo prepare ~/argo-research --symbol MSFT
# Host reads runs/RUN_ID/context.md and fills the generated proposal template.
argo stage ~/argo-research --run RUN_ID --proposal /path/to/proposal.json
```

`RUN_ID` is the ID returned by prepare. There is no hidden `argo analyze` command:
reasoning and evidence gathering occur in the user's host. The prepared context
includes the knowledge pack and portfolio status; source checking and financial
interpretation remain the host's responsibility. Use `insufficient_evidence` if
necessary rather than creating a valuation to satisfy a template.

## 4. Review before archival

Inspect `runs/RUN_ID/report.md` and `changes.json`. Check source passages, period
comparability, calculations, assumptions and unresolved questions. The current
harness checks structure/references and point-value margin arithmetic; it does not
verify every financial calculation or scenario. After review, the operator may run:

```bash
argo apply ~/argo-research --run RUN_ID
```

This archives research and its calendar index entry. It does not approve a trade.
Live host execution and real IBKR transport have not been end-to-end verified by
this fixture. Broker access is unnecessary for company-only research. The current
prepare command requires a verified earnings event; ad hoc company research without
an earnings event is not yet a separate CLI task type.
