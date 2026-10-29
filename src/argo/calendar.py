"""Release-aware planning: an estimate is never treated as a published report."""
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from urllib.parse import urlsplit
from .storage import ArgoError, identifier, number, timestamp


def source_url(value):
    if not isinstance(value, str):
        raise ArgoError("Source URL must be an HTTPS URL")
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ArgoError("Source URL must be HTTPS with no embedded credentials")
    return value


def watchlist_entries(data):
    if data.get("version") != 1:
        raise ArgoError("Unsupported watchlist version")
    try:
        ZoneInfo(data["timezone"])
    except (KeyError, ZoneInfoNotFoundError) as exc:
        raise ArgoError("watchlist.timezone must be an IANA timezone") from exc
    symbols = data.get("symbols")
    if not isinstance(symbols, list):
        raise ArgoError("watchlist.symbols must be a list")
    seen = set()
    for entry in symbols:
        symbol = identifier(entry.get("symbol"))
        if symbol in seen:
            raise ArgoError(f"Duplicate watchlist symbol: {symbol}")
        seen.add(symbol)
        if not isinstance(entry.get("company"), str) or not entry["company"].strip():
            raise ArgoError("Watchlist entry needs company name")
        if not isinstance(entry.get("enabled", True), bool):
            raise ArgoError("enabled must be boolean")
        source_url(entry.get("ir_url"))
        if "theme_weights" in entry:
            weights = entry["theme_weights"]
            if not isinstance(weights, dict) or not weights:
                raise ArgoError("Candidate theme_weights must be a nonempty object")
            total = sum(number(v, identifier(k), maximum=1) for k, v in weights.items())
            if abs(total - 1) > 0.000001:
                raise ArgoError("Candidate disjoint theme fractions must sum to 1")

    return symbols


def release_plan(watchlist, calendar, now, reviewed=None):
    entries = watchlist_entries(watchlist)
    enabled = {x["symbol"] for x in entries if x.get("enabled", True)}
    if calendar.get("version") != 1 or not isinstance(calendar.get("events"), list):
        raise ArgoError("Calendar requires version=1 and events list")
    reviewed = reviewed or set()
    result, ids = [], set()
    for event in calendar["events"]:
        event_id, symbol = identifier(event.get("id")), identifier(event.get("symbol"))
        if event_id in ids:
            raise ArgoError(f"Duplicate earnings event id: {event_id}")
        ids.add(event_id)
        source_url(event.get("source_url"))
        expected = timestamp(event["expected_at"]) if event.get("expected_at") else None
        released = timestamp(event["released_at"]) if event.get("released_at") else None
        checked = timestamp(event.get("verified_at"))
        if checked > now:
            raise ArgoError("Calendar verification is in the future")
        if released and released > checked:
            raise ArgoError("Cannot verify a release before it was published")
        if event.get("source_kind") not in {"official_ir", "official_filing"}:
            raise ArgoError("Confirmed calendar events need an official source")
        if not isinstance(event.get("period"), str) or not event["period"].strip():
            raise ArgoError("Event needs a reporting period")
        if symbol not in enabled:
            continue
        if event_id in reviewed:
            status = "reviewed"
        elif released and released <= now:
            status = "released"
        elif expected and expected > now:
            status = "scheduled"
        else:
            status = "release_unverified"
        result.append({**event, "status": status})
    # Missing a date/provider result must remain visible, not silently disappear.
    present = {event["symbol"] for event in result}
    for symbol in sorted(enabled - present):
        result.append({"symbol": symbol, "status": "date_unknown"})
    return result
