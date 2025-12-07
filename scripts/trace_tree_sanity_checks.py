"""Basic sanity checks for JSONL trace trees.

This script is designed to work with the synthetic traces in
`examples/synthetic_traces/` as well as similarly-structured
JSONL logs.

It focuses on simple, structural checks that are often useful before
running more detailed instability analysis:

- monotonic timestamps per trace
- basic trace_id / span_id consistency
- detection of empty or extremely short sessions
- rough span fan-out statistics (how "bushy" traces are)

These checks are intentionally lightweight and advisory.

Example usage:

    python scripts/trace_tree_sanity_checks.py \
      --file examples/synthetic_traces/noisy_mixed_sessions.jsonl
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------


@dataclass
class Event:
    raw: Dict[str, Any]

    @property
    def trace_id(self) -> str:
        return str(self.raw.get("trace_id", ""))

    @property
    def span_id(self) -> str:
        return str(self.raw.get("span_id", ""))

    @property
    def timestamp(self) -> Optional[datetime]:
        ts = self.raw.get("timestamp")
        if not isinstance(ts, str):
            return None
        try:
            # tolerate trailing "Z" and millisecond precision
            if ts.endswith("Z"):
                ts = ts[:-1]
            return datetime.fromisoformat(ts)
        except ValueError:
            return None

    @property
    def parent_id(self) -> Optional[str]:
        parent = self.raw.get("parent_span_id") or self.raw.get("parent_id")
        if parent is None:
            return None
        return str(parent)


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


def load_events(path: str) -> List[Event]:
    events: List[Event] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            events.append(Event(obj))
    return events


def group_by_trace(events: Iterable[Event]) -> Dict[str, List[Event]]:
    traces: Dict[str, List[Event]] = defaultdict(list)
    for ev in events:
        traces[ev.trace_id].append(ev)
    return traces


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def check_timestamp_monotonicity(events: List[Event]) -> Tuple[bool, int]:
    """Return (is_monotonic, violations_count)."""
    prev: Optional[datetime] = None
    violations = 0
    for ev in events:
        ts = ev.timestamp
        if ts is None:
            continue
        if prev is not None and ts < prev:
            violations += 1
        prev = ts
    return violations == 0, violations


def compute_span_fanout(events: List[Event]) -> Dict[str, int]:
    """Return child count per span_id based on parent_span_id/parent_id."""
    children: Dict[str, int] = defaultdict(int)
    for ev in events:
        parent = ev.parent_id
        if parent:
            children[parent] += 1
    return children


def detect_short_sessions(
    traces: Dict[str, List[Event]],
    min_events: int = 3,
) -> List[str]:
    """Return trace_ids with fewer than `min_events` events."""
    return [tid for tid, evs in traces.items() if len(evs) < min_events]


# ---------------------------------------------------------------------------
# CLI / reporting
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run basic sanity checks on JSONL trace trees.",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to JSONL trace file.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    import sys

    args = parse_args(argv)

    events = load_events(args.file)
    if not events:
        print("No events loaded.")
        return

    traces = group_by_trace(events)
    num_events = len(events)
    num_traces = len(traces)
    print(f"Loaded {num_events} events across {num_traces} sessions.\n")

    # 1) Timestamp monotonicity
    non_mono = 0
    total_violations = 0
    for _tid, evs in traces.items():
        ok, violations = check_timestamp_monotonicity(evs)
        if not ok:
            non_mono += 1
            total_violations += violations
    print("[timestamp-monotonicity]")
    print(f"  sessions with violations: {non_mono}")
    print(f"  total violations        : {total_violations}")
    print()

    # 2) Span fan-out statistics
    fanouts: Counter[int] = Counter()
    for evs in traces.values():
        children = compute_span_fanout(evs)
        for count in children.values():
            fanouts[count] += 1

    print("[span-fanout]")
    if fanouts:
        for fan, cnt in sorted(fanouts.items()):
            print(f"  spans with {fan:2d} children: {cnt}")
    else:
        print(
            "  no parent-child relationships detected "
            "(no parent_span_id fields).",
        )
    print()

    # 3) Short sessions
    short = detect_short_sessions(traces, min_events=3)
    print("[short-sessions]")
    print(f"  sessions with < 3 events: {len(short)}")
    if len(short) <= 10:
        for tid in short:
            print(f"    - {tid}")
    else:
        print("    (too many to list)\n")


if __name__ == "__main__":  # pragma: no cover
    main()
