"""Mark a prepared AI Signal digest as delivered.

prepare_digest.py writes a delivery-mark.json file with the item IDs selected
for the digest. Run this script only after the digest has actually been shown or
sent successfully. That keeps retries from losing unseen items.

Usage:
    python scripts/mark_delivered.py --file ~/.ai-signal/payload/delivery-mark.json
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


USER_DIR = Path.home() / ".ai-signal"
SEEN_PATH = USER_DIR / "seen.json"
DEFAULT_MARK_PATH = USER_DIR / "payload" / "delivery-mark.json"
SEEN_RETENTION_DAYS = 14


def configure_stdio():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def load_seen():
    seen = {}
    if SEEN_PATH.exists():
        try:
            seen = json.loads(SEEN_PATH.read_text("utf-8"))
        except Exception:
            seen = {}
    for key in ("tweets", "episodes", "papers", "articles"):
        seen.setdefault(key, {})
    return seen


def save_seen(seen):
    cutoff = (datetime.now(timezone.utc) - timedelta(days=SEEN_RETENTION_DAYS)).isoformat()
    for key in ("tweets", "episodes", "papers", "articles"):
        seen[key] = {k: v for k, v in seen.get(key, {}).items() if v > cutoff}
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEEN_PATH.write_text(json.dumps(seen, indent=2), encoding="utf-8")


def load_mark(path):
    data = json.loads(path.read_text("utf-8"))
    ids = data.get("ids", {})
    for key in ("tweets", "episodes", "papers", "articles"):
        ids.setdefault(key, {})
    return ids, data.get("labels") or {}


LABEL_RE = re.compile(r"^([A-Za-z]+)(\d+)$")


def expand_labels(raw):
    """Accept 'Paper1-Paper3' and 'X1-X5' as shorthand for the whole run.

    A digest that shows twenty items shouldn't need twenty comma-separated
    labels; that is where typos and omissions come from.
    """
    out = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" not in chunk:
            out.append(chunk)
            continue
        start, _, end = chunk.partition("-")
        m1, m2 = LABEL_RE.match(start.strip()), LABEL_RE.match(end.strip())
        # Only expand when both ends name the same kind, e.g. Paper1-Paper3.
        if not (m1 and m2) or m1.group(1).lower() != m2.group(1).lower():
            out.append(chunk)
            continue
        prefix = m1.group(1)
        lo, hi = int(m1.group(2)), int(m2.group(2))
        if lo > hi:
            lo, hi = hi, lo
        out.extend(f"{prefix}{n}" for n in range(lo, hi + 1))
    return out


def select_shown(ids, labels, shown):
    """Keep only the items the digest actually printed.

    The payload is deliberately wider than the digest — 30 papers can go in and
    3 come out. Marking the whole payload buried the other 27 forever, since a
    seen item never returns. The Agent knows what it printed, so it passes the
    labels back (X1, P2, Paper3, B1) and only those get marked.

    Unknown labels are reported rather than ignored: silently dropping them
    would recreate the same silent data loss in the other direction.
    """
    picked = {kind: {} for kind in ids}
    unknown = []
    for raw in shown:
        label = raw.strip()
        if not label:
            continue
        entry = labels.get(label) or labels.get(label.upper())
        if not entry:
            unknown.append(label)
            continue
        kind, item_id = entry.get("kind"), entry.get("id")
        stamp = ids.get(kind, {}).get(item_id)
        if stamp is None:
            unknown.append(label)
            continue
        picked.setdefault(kind, {})[item_id] = stamp
    return picked, unknown


def main():
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default=str(DEFAULT_MARK_PATH),
                        help="Path to delivery-mark.json")
    parser.add_argument("--shown", type=str, default="",
                        help="Labels the digest actually printed, comma-separated. "
                             "Ranges allowed: 'X1-X5,P1,Paper1-Paper3,B1'. Required "
                             "unless --all.")
    parser.add_argument("--all", action="store_true",
                        help="Mark every candidate. Only correct when the digest "
                             "really printed all of them.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be marked without writing seen.json")
    args = parser.parse_args()

    mark_path = Path(args.file).expanduser()
    if not mark_path.exists():
        print(json.dumps({"status": "error", "error": f"Missing mark file: {mark_path}"}))
        sys.exit(1)

    ids, labels = load_mark(mark_path)

    # Refuse rather than guess. Marking everything buries items the user never
    # saw and a seen item never returns; marking nothing only makes tomorrow
    # repeat them. Between a silent loss and a visible repeat, take the repeat.
    if not args.shown.strip() and not args.all:
        print(json.dumps({
            "status": "error",
            "error": "--shown is required (or --all if the digest printed everything)",
            "hint": "pass the labels you printed, e.g. --shown 'X1-X4,P1,Paper1-Paper3,B1'",
            "available": {kind: len(v) for kind, v in ids.items()},
        }, ensure_ascii=False, indent=2))
        sys.exit(2)

    unknown = []
    if args.shown.strip():
        ids, unknown = select_shown(ids, labels, expand_labels(args.shown))
    counts = {kind: len(values) for kind, values in ids.items()}
    result = {"status": "ok", "marked": counts}
    if unknown:
        result["unknown_labels"] = unknown

    if args.dry_run:
        result["dry_run"] = True
        print(json.dumps(result, indent=2))
        return

    seen = load_seen()
    for kind, values in ids.items():
        seen.setdefault(kind, {}).update(values)
    save_seen(seen)

    result["seen_path"] = str(SEEN_PATH)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
