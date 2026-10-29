# Data contracts (v1)

All quantities in one workspace use the policy currency. No FX conversion is inferred.
Use full ISO 8601 timestamps with timezone. Sample files in `examples/` are fictional.

## Workspace

- `watchlist.json`: version 1, IANA timezone, symbols [{symbol, company, ir_url, enabled, theme_weights (optional)}].
  For an unheld candidate, supply disjoint theme fractions to enable addition checks.
- `earnings.json`: version 1, events [{id, symbol, period, expected_at (nullable),
  released_at (nullable), source_url, source_kind (official_ir/official_filing), verified_at}].
  Expected time alone never establishes release. A watchlist symbol with no event is `date_unknown`.
- `policy.json`: version 1, currency, max_snapshot_age_hours, single_stock_max,
  minimum_margin_of_safety, role_ranges {core/satellite/cash: [lower,upper]},
  theme_limits {theme: fraction}, frozen_themes [theme]. Fractions are 0–1.
- `portfolio.json`: version 1, as_of, currency, cash {available, reserved},
  positions [{symbol, asset_type (stock/etf), market_value, role (core/satellite),
  theme_weights {theme: fraction}}]. Theme fractions are **disjoint** and must sum to 1.
  ETF fractions are supplied, not automatically looked through by Argo.
  Remove this file when portfolio is unavailable; do not fabricate zero holdings.
- `knowledge/*.md`: selected task context; basename wikilinks must resolve.

Denominator = sum(position market values) + available cash. Reserved cash is excluded
from both numerator and denominator of investable role/theme weights; still reported
in account value. This is a deliberately simple **example policy**, not the author's IPS.

Rule IDs: P-SNAPSHOT (freshness), P-DATA (completeness), P-SINGLE-STOCK,
P-CORE, P-SATELLITE, P-CASH, P-THEME, P-FROZEN, P-MARGIN.
The initial conservative template blocks `consider` while portfolio data/limit findings
are unresolved. Theme freezes are informational in the portfolio summary and block only
candidates with positive exposure to the frozen theme. An unknown candidate classification
blocks `consider`; it does not mean zero exposure. No rule authorizes a transaction.

## Agent proposal

Use the prepared run's proposal-template.json for the exact response shape:

- run_id, symbol, event_id must match the prepared task.
- evidence: id, HTTPS url, kind, published_at, accessed_at, excerpt.
- claims: text and evidence_ids, resolving to supplied sources.
- analysis: business_quality and bear_case.
- valuation: price, intrinsic_value, currency, price_as_of, assumptions[]; null is allowed
  for insufficient_evidence. That stance also permits empty evidence/claims rather than fabricated facts.
  Publication and price times cannot be later than the task time; access time may be later
  because retrieval happens during execution, but cannot be in the future at validation.
- decision: stance (wait/consider/reduce/insufficient_evidence), rationale,
  policy_refs[], position_purpose (long_term/short_term/undecided), exit_conditions[].
- limitations[].

Argo recomputes the margin under the supplied intrinsic-value assumption. It does not
validate that valuation, authenticate an official-looking URL, fetch sources on stage,
or establish semantic correctness of a claim. Source content must be checked by the host
and reviewer. `consider` is blocked on stale/missing context, policy violations or
insufficient configured margin. Other stances can report incomplete information.

## Synthetic expected findings

`examples/portfolio.json`: account 100,000; reserved 5,000; investable 95,000.
Core = 60,000/95,000 (63.16%); satellite = 25,000/95,000 (26.32%); cash = 10,000/95,000 (10.53%).
Technology = (60,000×0.30 + 20,000)/95,000 = 40%.
Expected findings: P-SINGLE-STOCK (AURX), P-THEME (technology), P-FROZEN.
No core/satellite/cash band violation. AURX margin scenario = (120−80)/120 = 33⅓%;
portfolio context still blocks additions. These are test fixtures, not investment recommendations.
