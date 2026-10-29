"""Build portfolio context without giving the model arithmetic ownership."""
from .storage import ArgoError, identifier, number, timestamp

POLICY_REFS = {
    "P-SNAPSHOT", "P-SINGLE-STOCK", "P-CORE", "P-SATELLITE", "P-CASH",
    "P-THEME", "P-FROZEN", "P-MARGIN", "P-DATA",
}


def validate_policy(policy):
    if policy.get("version") != 1:
        raise ArgoError("Unsupported policy version")
    if not isinstance(policy.get("currency"), str) or len(policy["currency"]) != 3:
        raise ArgoError("policy.currency must be a three-letter currency")
    number(policy.get("max_snapshot_age_hours"), "max_snapshot_age_hours", minimum=1)
    for key in ("single_stock_max", "minimum_margin_of_safety"):
        number(policy.get(key), key, maximum=1)
    if set(policy.get("role_ranges", {})) != {"core", "satellite", "cash"}:
        raise ArgoError("role_ranges must define core, satellite and cash")
    for role, limits in policy["role_ranges"].items():
        if not isinstance(limits, list) or len(limits) != 2:
            raise ArgoError(f"role_ranges.{role} must be [min, max]")
        lo, hi = (number(x, role, maximum=1) for x in limits)
        if lo > hi:
            raise ArgoError(f"role_ranges.{role}: min exceeds max")
    if not isinstance(policy.get("theme_limits"), dict):
        raise ArgoError("theme_limits must be an object")
    for theme, limit in policy["theme_limits"].items():
        identifier(theme)
        number(limit, theme, maximum=1)
    if not isinstance(policy.get("frozen_themes"), list) or any(
        not isinstance(t, str) for t in policy["frozen_themes"]
    ):
        raise ArgoError("frozen_themes must be a string list")
    return policy


def portfolio_context(portfolio, policy, now):
    validate_policy(policy)
    findings = []

    def add(ref, message, block=True):
        findings.append({"rule_id": ref, "message": message, "blocks_addition": block})

    if portfolio is None:
        add("P-DATA", "Portfolio not supplied; holdings are unknown, not an empty account")
        return {"status": "incomplete", "findings": findings, "additions_blocked": True}
    if portfolio.get("version") != 1 or portfolio.get("currency") != policy["currency"]:
        raise ArgoError("Portfolio version/currency must match policy; normalize currencies explicitly")
    snapshot_time = timestamp(portfolio.get("as_of"))
    age = (now - snapshot_time).total_seconds() / 3600
    if age < 0:
        raise ArgoError("Portfolio snapshot is from the future")
    if age > policy["max_snapshot_age_hours"]:
        add("P-SNAPSHOT", "Portfolio snapshot is stale")
    cash = portfolio.get("cash", {})
    available = number(cash.get("available"), "cash.available")
    reserved = number(cash.get("reserved"), "cash.reserved")
    positions = portfolio.get("positions")
    if not isinstance(positions, list):
        raise ArgoError("positions must be a list; empty is explicit zero holdings")
    symbols, totals, themes = set(), {"core": 0., "satellite": 0., "cash": available}, {}
    normalized = []
    for pos in positions:
        symbol = identifier(pos.get("symbol"))
        if symbol in symbols:
            raise ArgoError(f"Duplicate holding: {symbol}")
        symbols.add(symbol)
        if pos.get("role") not in {"core", "satellite"}:
            raise ArgoError(f"{symbol}: role must be core or satellite")
        if pos.get("asset_type") not in {"stock", "etf"}:
            raise ArgoError(f"{symbol}: asset_type must be stock or etf")
        value = number(pos.get("market_value"), f"{symbol}.market_value")
        totals[pos["role"]] += value
        weights = pos.get("theme_weights")
        if not isinstance(weights, dict) or not weights:
            add("P-DATA", f"{symbol}: theme exposure unknown")
            weights = {}
        # This template uses disjoint theme fractions, not overlapping labels.
        fractions = {identifier(k): number(v, f"{symbol}.{k}", maximum=1) for k, v in weights.items()}
        if abs(sum(fractions.values()) - 1) > 0.000001:
            add("P-DATA", f"{symbol}: disjoint theme fractions must sum to 1")
        for theme, weight in fractions.items():
            themes[theme] = themes.get(theme, 0.) + value * weight
        normalized.append({**pos, "market_value": value})
    eligible = sum(totals.values())
    if eligible <= 0:
        raise ArgoError("Investable denominator must be positive")
    for pos in normalized:
        if pos["asset_type"] == "stock" and pos["market_value"] / eligible > policy["single_stock_max"]:
            add("P-SINGLE-STOCK", f"{pos['symbol']}: single-stock weight exceeds policy")
    roles = {role: value / eligible for role, value in totals.items()}
    for role, value in roles.items():
        lo, hi = policy["role_ranges"][role]
        if not lo <= value <= hi:
            add("P-" + role.upper(), f"{role}: role weight outside configured band")
    exposures = {theme: value / eligible for theme, value in themes.items()}
    for theme, limit in policy["theme_limits"].items():
        if exposures.get(theme, 0.) > limit:
            add("P-THEME", f"{theme}: theme weight exceeds policy")
    # A freeze is an explicit user rule, not inferred from a market prediction.
    for theme in policy["frozen_themes"]:
        add("P-FROZEN", f"{theme}: additions in this theme are frozen", block=False)
    incomplete = any(f["rule_id"] in {"P-DATA", "P-SNAPSHOT"} for f in findings)
    return {
        "status": "incomplete" if incomplete else "ready",
        "snapshot_as_of": portfolio["as_of"], "currency": portfolio["currency"],
        "investable_value": eligible, "reserved_cash_excluded": reserved,
        "account_value": eligible + reserved, "role_weights": roles,
        "theme_weights": exposures, "findings": findings,
        "additions_blocked": any(f["blocks_addition"] for f in findings),
        "classification_note": "Theme fractions supplied by user; Argo does not infer ETF holdings",
    }
