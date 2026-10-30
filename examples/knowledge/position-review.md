# Workflow: review portfolio fit

Input: timestamped positions, currency, cash purposes, policy and explicit exposure mappings. State the denominator and distinguish reserved funds from investable assets. Review current issuer and theme concentration, fund look-through and cross-account overlap where supported. Missing mappings must remain visible. Describe the role of the contemplated position and separately model hypothetical changes if sufficient data and a suitable tool exist. Argo currently computes snapshot context, not order fills or correlations. No concept note overrides the user’s policy; no account absence implies zero holdings.

Related: [[concentration]] · [[risk-and-permanent-loss]] · [[buy-review]]

## Portfolio-fit template

1. Snapshot time, currency and investable denominator with reserved funds excluded as configured.
2. Issuer, fund and theme exposures, classification sources and unmapped amounts.
3. Policy comparisons with exact IDs and separately stated user judgment.
4. Hypothetical changes only when separately calculated; report missing information and do not infer trading capacity from an absent account.

## Provenance

Adapted concept: 仓位. Source orientation: Editorial workflow synthesis of Fisher, Lynch and Marks. Original English paraphrase and editorial synthesis; not a quotation or a chapter reproduction. Source scope and reading pointers are documented in the repository’s docs/knowledge.md.
