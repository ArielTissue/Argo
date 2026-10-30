# Installation

## Python harness

Python 3.11+ is required. Clone the repository, create a virtual environment, then
`python -m pip install .`. The command is `argo`; `python -m argo` also works.
No global agent settings are changed by installation.

For development: `python -m pip install -e .` and
`python -m unittest discover -s tests -v`.

Initialize a **new empty** private workspace with `argo init /path/to/workspace`.
Do not point init at an existing Obsidian vault. The initializer never overwrites
an existing nonempty directory. The default knowledge pack contains curated, source-oriented concepts and workflows;
company and portfolio inputs are synthetic. Import your own selected material separately.

## Optional local host plugin

The repository includes a portable `plugins/argo/plugin.json` manifest and
`skills/argo-research/SKILL.md`, plus a repo marketplace at
`.agents/plugins/marketplace.json`. In supported Codex local-plugin clients,
`codex plugin marketplace add .` registers this repository as a source.
Install Argo from that source in the desktop Plugins Directory and start a fresh session.
Host availability and policy can vary. This repository does not install or authenticate
IBKR on your behalf.

Official references (checked 2026-10-29):
- [Skills and MCP responsibilities](https://developers.openai.com/plugins/concepts/skills)
- [Local plugin packaging and marketplace installation](https://developers.openai.com/plugins/build/plugins)

The plugin packages instructions. It has no MCP server that impersonates another
plugin's authorization, and no hidden model/telemetry service. A standalone caller
can use the Python harness without installing a plugin, but must supply its own reasoning.

## Watchlist and calendar

Use `argo watchlist WORKSPACE --add SYMBOL --company NAME --ir-url HTTPS_URL`.
Edit versioned JSON directly for policy or bulk configuration. All examples are
provided in the wheel and the source checkout.

An enabled symbol without a verified event is returned as `date_unknown`. Your host
checks the company's official announcements and imports `earnings.json` using
`argo import-data`. An SEC filing date/deadline is not automatically an earnings
announcement date. Do not replace unknown dates with guesses.

## Scheduling

The CLI is callable by a user-controlled scheduler. The optional skill can also be
used in a host's scheduled task, subject to that host's tool availability and permissions.
This release creates no OS jobs, host automations or background processes. Verify a
manual run and the host's execution history before calling the flow unattended.
