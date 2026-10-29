# Local verification — 2026-10-29–30 (Asia/Shanghai)

- Python 3.11.7 on macOS arm64: 21 workflow behavior tests passed.
- Editable installation: passed.
- Wheel build and clean virtual-environment installation: passed.
- Installed `argo demo` outside the source checkout: passed, explicitly fixture-replay.
- Installed watchlist addition and unknown-date planning: passed.
- Runtime dependency metadata: none. PyYAML was used only by the external skill validator.
- Skill frontmatter validation: passed.
- JSON syntax and source-only credential/private-path pattern checks: passed.
- Finance sample arithmetic and initial expected findings independently reviewed;
  candidate-specific theme-freeze behavior was corrected and covered by tests.

Not verified: live IBKR transport/authentication, host-plugin installation UI, live LLM
analysis, automatic calendar-provider refresh, scheduled execution, or cross-platform CI.
CI configuration covers Python 3.11–3.13 but has not run remotely.

Tests establish software behavior on synthetic data, not investment outcomes or source truth.
Initial GitHub CLI authentication returned HTTP 401. The owner renewed authentication
on 2026-10-30 (Asia/Shanghai); publication proceeds under the owner's ArielTissue account.
Remote workflow results are tracked in GitHub Actions separately from these local checks.
