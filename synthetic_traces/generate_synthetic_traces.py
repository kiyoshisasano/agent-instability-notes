"""Generate synthetic JSONL traces for agent-instability-notes.

This script intentionally stays framework-agnostic. It emits small JSON objects
(1 per line) that can be used with the notebooks and metric scripts in this repo.

Usage examples:

  # Long-horizon toy traces (default)
  python generate_synthetic_traces.py --variant long_horizon --sessions 3 --turns 30 \
    > long_horizon_traces.jsonl

  # Noisy mixed sessions
  python generate_synthetic_traces.py --variant noisy_mixed --sessions 5 --noise medium \
    > noisy_mixed.jsonl

  # Minimal correction-loop traces
  python generate_synthetic_traces.py --variant simple_correction_loop --sessions 2 \
    > simple_loops.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, List


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


@dataclass
class Event:
    timestamp: datetime
    trace_id: str
    span_id: str
    component: str
    event_type: str
    execution_stage: str
    payload: Dict

    def to_json(self) -> str:
        obj = {
            "timestamp": self.timestamp.isoformat(timespec="milliseconds") + "Z",
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "component": self.component,
            "event_type": self.event_type,
            "execution_stage": self.execution_stage,
            "payload": self.payload,
        }
        return json.dumps(obj, ensure_ascii=False)


def _rand_id(prefix: str, width: int = 8) -> str:
    return f"{prefix}{random.randrange(16 ** width):0{width}x}"


def _base_start_time() -> datetime:
    # Arbitrary fixed base so runs are comparable but still distinct per run
    return datetime(2025, 1, 1, 10, 0, 0) + timedelta(seconds=random.randint(0, 60))


# ---------------------------------------------------------------------------
# Variant: long_horizon
# ---------------------------------------------------------------------------


def generate_long_horizon_session(trace_idx: int, turns: int, noise: str) -> Iterable[Event]:
    base = _base_start_time()
    trace_id = f"lh_{trace_idx:03d}"

    ts = base
    span_counter = 0

    def emit(component: str, event_type: str, stage: str, payload: Dict) -> Event:
        nonlocal ts, span_counter
        span_counter += 1
        # Small random gap between events
        gap_ms = random.randint(20, 120)
        ts = ts + timedelta(milliseconds=gap_ms)
        return Event(
            timestamp=ts,
            trace_id=trace_id,
            span_id=f"{trace_id}_s{span_counter:04d}",
            component=component,
            event_type=event_type,
            execution_stage=stage,
            payload=payload,
        )

    # Session init
    yield emit(
        "system",
        "session_init",
        "init",
        {"session_id": f"sess_{trace_id}", "variant": "long_horizon"},
    )

    # Synthetic user goal
    yield emit(
        "user",
        "user_message",
        "input",
        {
            "turn": 1,
            "content": "Run a multi-step checklist and keep it stable over time.",
        },
    )

    # Parameters controlling wobble
    if noise == "low":
        drift_turn = random.randint(max(3, turns // 4), max(4, turns // 3))
    elif noise == "high":
        drift_turn = random.randint(2, max(3, turns // 5))
    else:  # medium
        drift_turn = random.randint(max(3, turns // 5), max(4, turns // 3))

    recovery_turn = min(turns - 3, drift_turn + random.randint(2, 5))
    relapse_turn = min(turns - 1, recovery_turn + random.randint(3, 8))

    # Main loop
    for turn in range(1, turns + 1):
        # baseline latency pattern
        base_latency = random.randint(90, 160)

        # add drift-related noise
        if drift_turn <= turn < recovery_turn:
            base_latency += random.randint(60, 220)
        elif recovery_turn <= turn < relapse_turn:
            base_latency += random.randint(-30, 40)
        elif relapse_turn <= turn:
            base_latency += random.randint(80, 260)

        # reasoning step
        yield emit(
            "agent",
            "reason_step",
            "processing",
            {
                "turn": turn,
                "latency_ms": base_latency,
                "note": _reason_note(turn, drift_turn, recovery_turn, relapse_turn),
            },
        )

        # occasionally add a small self-check / correction span
        if turn in (drift_turn + 1, recovery_turn, relapse_turn):
            yield emit(
                "agent",
                "self_check",
                "recovery",
                {
                    "turn": turn,
                    "kind": "lightweight_correction",
                    "latency_ms": random.randint(80, 180),
                },
            )

    # Final outcome
    final_status = "stable" if relapse_turn > turns else "relapse_after_recovery"
    yield emit(
        "system",
        "session_end",
        "complete",
        {
            "turns": turns,
            "drift_turn": drift_turn,
            "recovery_turn": recovery_turn,
            "relapse_turn": relapse_turn,
            "final_status": final_status,
        },
    )


def _reason_note(turn: int, drift: int, recovery: int, relapse: int) -> str:
    if turn < drift:
        return "baseline pattern, stable"
    if drift <= turn < recovery:
        return "growing deviation, early instability"
    if recovery <= turn < relapse:
        return "temporarily stabilized after correction"
    return "late-stage wobble / relapse"


# ---------------------------------------------------------------------------
# Variant: simple_correction_loop
# ---------------------------------------------------------------------------


def generate_simple_correction_loop_session(trace_idx: int) -> Iterable[Event]:
    base = _base_start_time()
    trace_id = f"loop_{trace_idx:03d}"
    ts = base
    span_counter = 0

    def emit(component: str, event_type: str, stage: str, payload: Dict) -> Event:
        nonlocal ts, span_counter
        span_counter += 1
        ts = ts + timedelta(milliseconds=random.randint(40, 140))
        return Event(
            timestamp=ts,
            trace_id=trace_id,
            span_id=f"{trace_id}_s{span_counter:04d}",
            component=component,
            event_type=event_type,
            execution_stage=stage,
            payload=payload,
        )

    # Init + user
    yield emit("system", "session_init", "init", {"session_id": f"sess_{trace_id}"})
    yield emit(
        "user",
        "user_message",
        "input",
        {"turn": 1, "content": "Create a short checklist with exactly 3 items."},
    )

    # Stable first step
    yield emit(
        "agent",
        "agent_step",
        "processing",
        {
            "turn": 1,
            "latency_ms": random.randint(200, 320),
            "summary": "Initial 3-item checklist created.",
        },
    )

    # Drift-like step
    yield emit(
        "agent",
        "drift_like",
        "processing",
        {
            "turn": 2,
            "latency_ms": random.randint(260, 380),
            "note": "Checklist grows to 6 items, constraint partially dropped.",
        },
    )

    # Correction
    yield emit(
        "agent",
        "correction",
        "recovery",
        {
            "turn": 3,
            "kind": "self_check",
            "latency_ms": random.randint(160, 260),
            "note": "Re-read instruction and compress back to 3 items.",
        },
    )

    # Stabilized step
    yield emit(
        "agent",
        "agent_step",
        "output",
        {
            "turn": 4,
            "latency_ms": random.randint(200, 320),
            "summary": "3-item checklist, constraints respected.",
            "stability_tag": "recovered",
        },
    )

    yield emit(
        "system",
        "session_end",
        "complete",
        {
            "turns": 4,
            "instability_signals": 1,
            "corrections": 1,
            "final_status": "completed_after_correction",
        },
    )


# ---------------------------------------------------------------------------
# Variant: noisy_mixed
# ---------------------------------------------------------------------------


def generate_noisy_mixed_session(trace_idx: int, noise: str) -> Iterable[Event]:
    # Compose from a few small patterns: stable, corrected, incomplete.
    mode = random.choice(["stable", "corrected", "incomplete"])
    if noise == "high":
        # bias toward unstable shapes
        mode = random.choice(["corrected", "incomplete", "incomplete"])

    base = _base_start_time()
    trace_id = f"mix_{trace_idx:03d}"
    ts = base
    span_counter = 0

    def emit(component: str, event_type: str, stage: str, payload: Dict) -> Event:
        nonlocal ts, span_counter
        span_counter += 1
        ts = ts + timedelta(milliseconds=random.randint(30, 180))
        return Event(
            timestamp=ts,
            trace_id=trace_id,
            span_id=f"{trace_id}_s{span_counter:04d}",
            component=component,
            event_type=event_type,
            execution_stage=stage,
            payload=payload,
        )

    # Common start
    yield emit("system", "session_init", "init", {"session_id": f"sess_{trace_id}"})
    yield emit(
        "user",
        "user_message",
        "input",
        {"content": "Run a small multi-step task.", "approx_length": "short"},
    )

    if mode == "stable":
        # Straightforward 2-step sequence
        yield emit(
            "agent",
            "agent_step",
            "processing",
            {"turn": 1, "latency_ms": random.randint(150, 260)},
        )
        yield emit(
            "agent",
            "agent_step",
            "output",
            {"turn": 2, "latency_ms": random.randint(150, 260)},
        )
        yield emit(
            "system",
            "session_end",
            "complete",
            {"status": "ok", "pattern": "stable"},
        )
    elif mode == "corrected":
        # Small hallucination followed by correction
        yield emit(
            "agent",
            "agent_step",
            "processing",
            {"turn": 1, "latency_ms": random.randint(180, 320)},
        )
        yield emit(
            "agent",
            "drift_like",
            "processing",
            {
                "turn": 2,
                "latency_ms": random.randint(220, 380),
                "note": "off-topic or low-quality output",
            },
        )
        yield emit(
            "monitor",
            "warning",
            "monitoring",
            {"reason": "content_mismatch"},
        )
        yield emit(
            "agent",
            "correction",
            "recovery",
            {"action": "retry", "turn": 3},
        )
        yield emit(
            "agent",
            "agent_step",
            "output",
            {
                "turn": 4,
                "latency_ms": random.randint(170, 300),
                "stability_tag": "recovered",
            },
        )
        yield emit(
            "system",
            "session_end",
            "complete",
            {"status": "corrected", "pattern": "corrected"},
        )
    else:  # incomplete
        # Missing-detail scenario; session ends early
        yield emit(
            "agent",
            "agent_step",
            "processing",
            {"turn": 1, "latency_ms": random.randint(150, 280)},
        )
        yield emit(
            "monitor",
            "warning",
            "monitoring",
            {"reason": "missing_required_detail"},
        )
        # User does not respond or system stops
        yield emit(
            "system",
            "session_end",
            "complete",
            {"status": "incomplete", "pattern": "incomplete"},
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic JSONL traces for agent-instability-notes.",
    )
    parser.add_argument(
        "--variant",
        choices=["long_horizon", "simple_correction_loop", "noisy_mixed"],
        default="long_horizon",
        help="Which synthetic pattern to generate.",
    )
    parser.add_argument(
        "--sessions",
        type=int,
        default=1,
        help="Number of sessions (traces) to generate.",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=30,
        help="Approximate number of turns for long_horizon variant.",
    )
    parser.add_argument(
        "--noise",
        choices=["low", "medium", "high"],
        default="medium",
        help="Noise level (used by long_horizon / noisy_mixed).",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)

    random.seed()

    events: Iterable[Event]
    for i in range(args.sessions):
        if args.variant == "long_horizon":
            events = generate_long_horizon_session(i, args.turns, args.noise)
        elif args.variant == "simple_correction_loop":
            events = generate_simple_correction_loop_session(i)
        else:  # noisy_mixed
            events = generate_noisy_mixed_session(i, args.noise)

        for ev in events:
            sys.stdout.write(ev.to_json() + "\n")


if __name__ == "__main__":  # pragma: no cover
    main()
