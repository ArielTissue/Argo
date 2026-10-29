"""Command-line entry points; no credential collection or implicit model calls."""
import argparse
from importlib.resources import files
from pathlib import Path
import sys

from .calendar import source_url, watchlist_entries
from .context import portfolio_context
from .storage import ArgoError, atomic_write, child, identifier, json_text, load, lock, timestamp, utcnow
from .workflow import apply, init_workspace, plan, prepare, stage, workspace_inputs


def main(argv=None):
    parser = argparse.ArgumentParser(prog="argo", description="Knowledge-grounded, portfolio-aware research harness")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "watchlist", "plan", "context", "prepare", "stage", "apply", "import-data"):
        p = sub.add_parser(name)
        p.add_argument("workspace", type=Path)
        if name in {"plan", "context", "prepare"}:
            p.add_argument("--as-of", help="Timezone-aware task timestamp; use current time for live work")
        if name == "watchlist":
            p.add_argument("--add", metavar="SYMBOL")
            p.add_argument("--remove", metavar="SYMBOL")
            p.add_argument("--company")
            p.add_argument("--ir-url")
        if name == "prepare":
            p.add_argument("--symbol", required=True)
        if name in {"stage", "apply"}:
            p.add_argument("--run", required=True)
        if name == "import-data":
            p.add_argument("--kind", choices=["portfolio", "calendar"], required=True)
            p.add_argument("--file", type=Path, required=True)
        if name == "stage":
            p.add_argument("--proposal", type=Path, required=True)
    p = sub.add_parser("demo", help="Run an explicitly labeled synthetic fixture replay; no AI/network/account")
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        command = args.command
        if command == "demo":
            root = init_workspace(args.output)
            task = prepare(root, "AURX", timestamp("2026-10-29T12:00:00Z"), mode="fixture-replay")
            proposal = __import__('json').loads(files("argo_examples").joinpath("proposal.json").read_text())
            proposal["run_id"] = task["run_id"]
            stage(root, task["run_id"], proposal)
            result = apply(root, task["run_id"])
            result.update({"mode": "fixture-replay", "workspace": str(root), "live_llm": False, "live_broker": False})
        else:
            root = args.workspace.expanduser().resolve()
            now = timestamp(args.as_of) if getattr(args, "as_of", None) else utcnow()
            if command == "init":
                result = {"workspace": str(init_workspace(root)), "data": "synthetic; replace before live use"}
            elif command == "watchlist":
                with lock(root):
                    path = child(root, "watchlist.json")
                    watchlist = load(path)
                    watchlist_entries(watchlist)
                    if args.add and args.remove:
                        raise ArgoError("Choose --add or --remove")
                    if args.add:
                        symbol = identifier(args.add.upper())
                        if not args.company or not args.ir_url:
                            raise ArgoError("--add needs --company and --ir-url")
                        if any(e['symbol'] == symbol for e in watchlist['symbols']):
                            raise ArgoError("Symbol already in watchlist")
                        watchlist['symbols'].append({"symbol": symbol, "company": args.company,
                                                     "ir_url": source_url(args.ir_url), "enabled": True})
                    elif args.remove:
                        symbol = identifier(args.remove.upper())
                        if not any(e['symbol'] == symbol for e in watchlist['symbols']):
                            raise ArgoError("Symbol not found")
                        watchlist['symbols'] = [e for e in watchlist['symbols'] if e['symbol'] != symbol]
                    watchlist_entries(watchlist)
                    if args.add or args.remove:
                        atomic_write(path, json_text(watchlist))
                    result = watchlist
            elif command == "import-data":
                data = load(args.file)
                with lock(root):
                    inputs = workspace_inputs(root)
                    if args.kind == "portfolio":
                        portfolio_context(data, inputs["policy.json"], now)
                        target = "portfolio.json"
                    else:
                        from .calendar import release_plan
                        release_plan(inputs["watchlist.json"], data, now)
                        target = "earnings.json"
                    atomic_write(child(root, target), json_text(data))
                    result = {"imported": target, "source_file": str(args.file),
                              "note": "Contract validated; source truth and provenance require review"}
            elif command == "plan":
                result = {"as_of": now.isoformat(), "events": plan(root, now)}
            elif command == "context":
                inputs = workspace_inputs(root)
                result = portfolio_context(inputs.get("portfolio.json"), inputs["policy.json"], now)
            elif command == "prepare":
                result = prepare(root, args.symbol, now)
            elif command == "stage":
                result = stage(root, args.run, load(args.proposal))
            elif command == "apply":
                result = apply(root, args.run)
        print(json_text(result), end="")
    except (ArgoError, KeyError, TypeError, OSError) as exc:
        print(f"argo: {exc}", file=sys.stderr)
        return 2
    return 0
