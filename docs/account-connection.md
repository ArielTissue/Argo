# Bring your own account connection

There are two separate boundaries:

1. The user installs/authenticates a broker plugin in their own agent host.
2. The host reads its account and converts the response into Argo's portfolio contract.

Downloading Argo does not transfer a hosted app session, OAuth token or broker access.
Do not put credentials or raw real-account responses in this repository.

## Hosted workflow

The bundled skill discovers the user's available account read tools. Actual tool names,
required arguments, response shapes and authentication depend on the connector.
The host normalizes a snapshot to `docs/data-contracts.md`, preserving the true as-of
time and currency. Do not invent missing data, count reserved funds twice or assume
ETF classifications are supplied by a position endpoint. A missing portfolio is unknown.

```bash
argo import-data ~/argo-workspace --kind portfolio --file /private/normalized-snapshot.json
argo context ~/argo-workspace
```

The imported file stays in the private workspace. No account is contacted by `demo`.

## Programmatic seam

`argo.brokers.HostBroker` accepts a host-authenticated `call_tool(name, arguments)` function.
Allowed operations are `get_account_positions`, `get_account_balances`,
`get_account_summary`, `get_price_snapshot`. The adapter is responsible for mapping
logical names to provider names and supplying required identifiers. It does not need to
expose a general-purpose tool executor to the analysis code.

This release tests the allowlist with a fake transport. It does **not** bundle a
standalone IBKR OAuth/MCP transport or auto-discover desktop app credentials.
The repository therefore cannot yet claim clone → authenticate → live account integration
has been verified for every host. That is a separately testable integration step.

The allowlist restricts this wrapper, not a host that independently has trading tools.
If the user's connector offers read-only permission scopes, use them. If it exposes
order tools in the host, denying those tools requires host controls as well as the
skill's instruction not to use them. Argo contains no order execution module.
