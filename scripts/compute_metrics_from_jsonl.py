"""Compute simple instability-focused metrics from JSONL traces.

This script is intentionally framework-agnostic and works with the
synthetic traces under `examples/synthetic_traces/` as well as
compatible JSONL logs from your own systems.

It reads JSON objects (one per line) from a file and prints a small
human-readable summary of:

- relative latency gaps
- recovery turn distance
- post-correction relapse rate
- basic session closure profile counts

The metrics are heuristic and meant for exploration, not production
SLOs.

Example usage:

    python scripts/compute_metrics_from_jsonl.py \
      --file examples/synthetic_traces/simple_correction_loop.jsonl

    python scripts/compute_metrics_from_jsonl.py \
      --file my_traces.jsonl --max-sessions 200
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Event:
    raw: Dict[str, Any]

    @property
    def trace_id(self) -> str:
        return str(self.raw.get("trace_id", ""))

    @property
    def event_type(self) -> str:
        return str(self.raw.get("event_type", ""))

    @property
    def component(self) -> str:
        return str(self.raw.get("component", ""))

    @property
    def phase(self) -> Optional[str]:
        # Optional, not required for all metrics
        phase = self.raw.get("phase")
        if phase is None and isinstance(self.raw.get("pld"), dict):
            phase = self.raw["pld"].get("phase")
        return phase

    @property
    def payload(self) -> Dict[str, Any]:
        obj = self.raw.get("payload")
        return obj if isinstance(obj, dict) else {}

    @property
    def latency_ms(self) -> Optional[float]:
        val = self.payload.get("latency_ms")
        try:
            return float(val) if val is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def turn(self) -> Optional[int]:
        val = self.payload.get("turn") or self.raw.get("turn")
        try:
            return int(val) if val is not None else None
        except (TypeError, ValueError):
            return None


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


def load_events(path: str, max_sessions: Optional[int] = None) -> List[Event]:
    """Load JSONL file into a list of Event objects.

    Stops after `max_sessions` distinct trace_ids if provided.
    """

    events: List[Event] = []
    seen_traces: set[str] = set()

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            ev = Event(obj)
            trace_id = ev.trace_id
            if trace_id:
                seen_traces.add(trace_id)
                if max_sessions is not None and len(seen_traces) > max_sessions:
                    break
            events.append(ev)

    return events


def group_by_trace(events: Iterable[Event]) -> Dict[str, List[Event]]:
    grouped: Dict[str, List[Event]] = defaultdict(list)
    for ev in events:
        grouped[ev.trace_id].append(ev)
    return grouped


# ---------------------------------------------------------------------------
# Metric 1: Relative latency gap
# ---------------------------------------------------------------------------


def compute_relative_latency_gaps(traces: Dict[str, List[Event]]) -> List[float]:
    """Compute relative latency gaps between consecutive events with latency.

    For each trace, we walk events in order and for each adjacent pair with
    defined `latency_ms`, we compute:

        gap = |a - b| / max(a, b, 1)

    Returns a list of gap values in [0, 1+].
    """

    gaps: List[float] = []
    for events in traces.values():
        prev: Optional[float] = None
        for ev in events:
            lat = ev.latency_ms
            if lat is None:
                continue
            if prev is not None:
                denom = max(prev, lat, 1.0)
                gaps.append(abs(prev - lat) / denom)
            prev = lat
    return gaps


# ---------------------------------------------------------------------------
# Metric 2: Recovery Turn Distance (heuristic)
# ---------------------------------------------------------------------------


def compute_recovery_turn_distances(traces: Dict[str, List[Event]]) -> List[int]:
    """Estimate turn distance from first drift-like event to first recovery.

    This uses a simple heuristic that looks for:

    - instability onset:  event_type == "drift_like"
    - recovery:           payload.stability_tag == "recovered"

    If both appear in order in the same trace, we compute:

        distance = recovered_turn - onset_turn

    and collect it into a list.
    """

    distances: List[int] = []

    for events in traces.values():
        onset_turn: Optional[int] = None
        for ev in events:
            if onset_turn is None and ev.event_type == "drift_like":
                onset_turn = ev.turn if ev.turn is not None else 0
                continue

            if onset_turn is not None:
                tag = ev.payload.get("stability_tag")
                if tag == "recovered":
                    end_turn = ev.turn if ev.turn is not None else onset_turn
                    distances.append(max(0, end_turn - onset_turn))
                    onset_turn = None

    return distances


# ---------------------------------------------------------------------------
# Metric 3: Post-correction relapse rate (heuristic)
# ---------------------------------------------------------------------------


def compute_post_correction_relapse_rate(traces: Dict[str, List[Event]]) -> Tuple[int, int]:
    """Compute (sessions_with_relapse, sessions_with_correction).

    Heuristic rules:
    - "correction" events are those with event_type in {"correction", "self_check"}.
    - a "relapse" is any later event with event_type == "drift_like".
    """

    with_correction = 0
    with_relapse = 0

    for events in traces.values():
        had_correction = False
        relapsed = False

        for ev in events:
            if not had_correction and ev.event_type in {"correction", "self_check"}:
                had_correction = True
                continue

            if had_correction and ev.event_type == "drift_like":
                relapsed = True
                break

        if had_correction:
            with_correction += 1
            if relapsed:
                with_relapse += 1

    return with_relapse, with_correction


# ---------------------------------------------------------------------------
# Metric 4: Session closure profile (very lightweight)
# ---------------------------------------------------------------------------


CLOSURE_LABELS = {
    "ok": "natural_completion",
    "completed_after_correction": "completed_after_correction",
    "corrected": "completed_after_correction",
    "incomplete": "incomplete",
    "error": "forced_stop",
}


def classify_session_closure(events: List[Event]) -> str:
    if not events:
        return "unknown"

    last = events[-1]
    payload = last.payload

    # explicit status field wins
    status = str(payload.get("status", "")).strip()
    final_status = str(payload.get("final_status", "")).strip()
    pattern = str(payload.get("pattern", "")).strip()

    for key in (status or None, final_status or None, pattern or None):
        if not key:
            continue
        label = CLOSURE_LABELS.get(key)
        if label:
            return label

    # fallback heuristics
    if last.event_type == "session_end":
        return "session_end_generic"
    if last.component == "user":
        return "user_abandonment"

    return "unknown"


def compute_session_closure_profile(traces: Dict[str, List[Event]]) -> Counter:
    counts: Counter = Counter()
    for events in traces.values():
        label = classify_session_closure(events)
        counts[label] += 1
    return counts


# ---------------------------------------------------------------------------
# CLI / reporting
# ---------------------------------------------------------------------------


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute simple instability metrics from JSONL traces.",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to JSONL trace file.",
    )
    parser.add_argument(
        "--max-sessions",
        type=int,
        default=None,
        help="Optional limit on number of sessions (trace_ids) to load.",
    )
    return parser.parse_args(argv)


def format_percent(numer: int, denom: int) -> str:
    if denom == 0:
        return "n/a"
    return f"{(numer / denom) * 100:.1f}%"  # noqa: WPS432


def main(argv: Optional[List[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    events = load_events(args.file, max_sessions=args.max_sessions)
    if not events:
        print("No events loaded.")
        return

    traces = group_by_trace(events)

    print(f"Loaded {len(events)} events across {len(traces)} sessions.\n")

    # 1) Relative latency gaps
    gaps = compute_relative_latency_gaps(traces)
    if gaps:
        print("[relative-latency-gap]")
        print(f"  samples: {len(gaps)}")
        print(f"  mean   : {statistics.mean(gaps):.3f}")
        print(f"  median : {statistics.median(gaps):.3f}")
        try:
            p90 = statistics.quantiles(gaps, n=10)[8]
            print(f"  p90    : {p90:.3f}")
        except Exception:
            pass
        print()

    # 2) Recovery Turn Distance
    rtd = compute_recovery_turn_distances(traces)
    if rtd:
        print("[recovery-turn-distance]")
        print(f"  episodes: {len(rtd)}")
        print(f"  mean    : {statistics.mean(rtd):.2f} turns")
        print(f"  median  : {statistics.median(rtd):.2f} turns")
        print()

    # 3) Post-correction relapse rate
    relapsed, corrected = compute_post_correction_relapse_rate(traces)
    if corrected > 0:
        print("[post-correction-relapse-rate]")
        print(f"  sessions with correction: {corrected}")
        print(f"  sessions with relapse   : {relapsed}")
        print(f"  relapse rate            : {format_percent(relapsed, corrected)}")
        print()

    # 4) Session closure profile
    profile = compute_session_closure_profile(traces)
    if profile:
        print("[session-closure-profile]")
        total_sessions = sum(profile.values())
        for label, count in profile.most_common():
            pct = format_percent(count, total_sessions)
            print(f"  {label:28s}: {count:3d}  ({pct})")
        print()


if __name__ == "__main__":  # pragma: no cover
    main()
