"""Workspace IO: bounded paths, optimistic concurrency, private run records."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile


class ArgoError(ValueError):
    """A user-actionable input or workflow error."""


def utcnow():
    return datetime.now(timezone.utc)


def timestamp(value):
    if not isinstance(value, str):
        raise ArgoError("Timestamp must be an ISO 8601 string with timezone")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ArgoError(f"Invalid timestamp: {value}") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ArgoError("Timestamp must include timezone")
    return result


def number(value, label, *, minimum=0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ArgoError(f"{label} must be a finite number")
    if value < minimum or (maximum is not None and value > maximum):
        raise ArgoError(f"{label} outside allowed range")
    return float(value)


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.^-]{0,79}", value):
        raise ArgoError("Invalid identifier; use letters, digits, dot, caret, hyphen or underscore")
    if ".." in value:
        raise ArgoError("Identifier cannot contain '..'")
    return value


def child(root, relative):
    root = Path(root).resolve()
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ArgoError("Path must be relative and remain inside workspace")
    path = root / rel
    # Reject symlinks rather than following them even when they currently point inside.
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ArgoError("Workspace paths cannot traverse symlinks")
    if not path.resolve().is_relative_to(root):
        raise ArgoError("Path escapes workspace")
    return path


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"),
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (OSError, ValueError) as exc:
        raise ArgoError(f"Cannot read JSON: {Path(path).name}: {exc}") from exc


def json_text(data):
    return json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def digest(path):
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".argo-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        Path(temp).unlink(missing_ok=True)


@contextmanager
def lock(workspace):
    p = child(workspace, ".argo.lock")
    try:
        fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ArgoError("Workspace busy; inspect .argo.lock before removing a stale lock") from exc
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        p.unlink(missing_ok=True)
