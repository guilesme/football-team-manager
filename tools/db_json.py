"""
db_json.py — JSON persistence layer with cross-platform file locking.
Manages read/write to data/db.json.

Supports Windows (msvcrt) and Unix/Linux/macOS (fcntl).
"""

import json
import os
import sys
from contextlib import contextmanager
from copy import deepcopy

_DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "db.json")
DB_PATH = os.environ.get("DB_PATH", _DEFAULT_DB_PATH)

DEFAULT_DB = {
    "config": {"ano": 2026, "moeda": "BRL"},
    "elenco": [],
    "calendario": [],
    "financeiro": []
}

# ---------------------------------------------------------------------------
# Cross-platform file locking
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    import msvcrt

    @contextmanager
    def _shared_lock(file_obj):
        msvcrt.locking(file_obj.fileno(), msvcrt.LK_LOCK, 1)
        try:
            yield
        finally:
            try:
                msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass

    @contextmanager
    def _exclusive_lock(file_obj):
        msvcrt.locking(file_obj.fileno(), msvcrt.LK_LOCK, 1)
        try:
            yield
        finally:
            try:
                msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass

else:
    import fcntl

    @contextmanager
    def _shared_lock(file_obj):
        fcntl.flock(file_obj, fcntl.LOCK_SH)
        try:
            yield
        finally:
            fcntl.flock(file_obj, fcntl.LOCK_UN)

    @contextmanager
    def _exclusive_lock(file_obj):
        fcntl.flock(file_obj, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(file_obj, fcntl.LOCK_UN)


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _ensure_dir():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def load_db() -> dict:
    """Load the JSON database, seeding with defaults if it doesn't exist."""
    _ensure_dir()
    if not os.path.exists(DB_PATH):
        save_db(deepcopy(DEFAULT_DB))
        return deepcopy(DEFAULT_DB)

    with open(DB_PATH, "r", encoding="utf-8") as f:
        with _shared_lock(f):
            data = json.load(f)
    return data


def save_db(data: dict):
    """Atomically write the JSON database."""
    _ensure_dir()
    tmp_path = DB_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        with _exclusive_lock(f):
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
            os.replace(tmp_path, DB_PATH)


def next_id(collection: list) -> int:
    """Generate the next integer ID for a collection."""
    if not collection:
        return 1
    return max(item.get("id", 0) for item in collection) + 1


def next_str_id(collection: list, prefix: str) -> str:
    """Generate the next string ID like 'match_001'."""
    if not collection:
        return f"{prefix}_001"
    nums = []
    for item in collection:
        sid = item.get("id", "")
        if isinstance(sid, str) and sid.startswith(prefix + "_"):
            try:
                nums.append(int(sid[len(prefix) + 1:]))
            except (ValueError, IndexError):
                pass
    n = max(nums) + 1 if nums else 1
    return f"{prefix}_{n:03d}"
