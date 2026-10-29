# Working on Argo

Argo combines knowledge context, company research, value analysis, portfolio context,
and human decisions. These are modules, not simulated employees.

- Examples must be newly authored and synthetic. Do not import private vaults, account
  snapshots, credentials, or personal policy into this repository.
- Core supports Python 3.11+ with the standard library. `python -m unittest discover -s tests -v`
  checks observable workflow behavior. Keep tests on the public module interface.
- Fixture replay is not a live LLM evaluation. A schema-valid answer is not proof of
  source accuracy, valuation correctness, or investment returns.
- Use timezone-aware timestamps. Never substitute an expected earnings date for an
  actual release. An absent portfolio is unknown, not a zero-position portfolio.
- Research writes are confined to the chosen workspace's output directory. Knowledge
  updates are a separate, explicit operation. Do not add order execution tools.
- Keep platform-provided orchestration/authentication distinct from Argo code.
