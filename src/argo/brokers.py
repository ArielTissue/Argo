"""A narrow seam for authenticated host tools, not a credential or OAuth client."""
from collections.abc import Callable, Mapping
from .storage import ArgoError

READ_TOOLS = frozenset({"get_account_positions", "get_account_balances", "get_account_summary", "get_price_snapshot"})


class HostBroker:
    """Use an existing host/MCP connection via a caller-supplied tool function.

    `call_tool(logical_name, arguments)` is supplied by the authenticated host.
    Provider-specific names and response normalization belong in that host adapter.
    This object cannot call order tools. It does not restrict the host's other tools.
    """
    def __init__(self, call_tool: Callable[[str, Mapping], object]):
        self._call_tool = call_tool

    def read(self, name: str, arguments: Mapping | None = None):
        if name not in READ_TOOLS:
            raise ArgoError(f"Broker operation is not allowed: {name}")
        return self._call_tool(name, dict(arguments or {}))

    def account_snapshot(self):
        return {name: self.read(name) for name in (
            "get_account_positions", "get_account_balances", "get_account_summary"
        )}
