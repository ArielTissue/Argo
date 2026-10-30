# Writing a useful earnings review

Use these sections within the existing proposal fields; this guide adds no JSON
keys or new CLI verdicts. Choose depth by materiality and available evidence. A
missing number is a limitation, not a reason to invent a comparable or estimate.

## Evidence and claims

Collect official releases/statements plus operating disclosures relevant to the
business. Record period, units, source date and location. Link every factual claim
to its evidence IDs. Separate year-over-year and sequential comparisons; reconcile
quarter lengths and cumulative versus standalone cash-flow statements. “Beat/miss”
needs a dated, clearly labeled consensus source; absence of estimates means no claim.

## analysis.business_quality

This string may contain Markdown subsections:

1. One-sentence business description and the question this release should answer.
2. Operating drivers: volume/price/mix, customer activity, relevant business KPIs,
   segments and guidance if disclosed. Explain the mechanism behind changes.
3. Profit bridge: show what improved and what offset it, using consistent denominators.
4. Cash quality: reconcile CFO, capital spending and adjustments such as SBC. Examine
   working capital and distinguish diagnostics from normalized cash forecasts.
5. Competitive advantage: what the new evidence supports, competing explanations,
   and what would falsify the proposed advantage.
6. Funding/capital allocation when material, with incomplete review left explicit.
7. Supported, contradicted and unresolved signals. Reference prior questions only
   when genuine prior research is available; do not invent continuity.

For each material paragraph, connect observation → possible explanation → implication
for the thesis → next check. Correlation or an accounting ratio is not proof of cause.
Do not confuse fee revenue with separately attributable profit, cardholders with
paid memberships, or membership sales mix with member-count mix.

## analysis.bear_case and valuation

Write causal failure paths, their cash/value impact and observable monitoring signals.
Use explicit scenarios and show which assumptions would have to change to support
price. Source facts and forecast choices separately. Disclose price time, cash-flow
basis, capital-structure treatment, terminal sensitivity and unsupported inputs.
The validator computes only the supplied point-value margin; the host must verify
all other financial calculations. Do not manufacture intrinsic value when evidence
is inadequate; use insufficient_evidence and valuation=null instead.

## decision and limitations

Conclude separately on business evidence, price assumptions and personal suitability.
If portfolio context exists, preserve its time and denominator and label hypothetical
weights. A missing account blocks claims of personal capacity, not company analysis.
List specific next evidence and reassessment conditions. Archival confirmation is a
file operation; the user makes any investment decision and handles execution separately.
