# Synthetic Traces

This directory contains **lightweight, fully synthetic log traces** designed to illustrate early-instability patterns in multi‑turn agents. These traces are intentionally simple: they use minimal fields (timestamp, trace ID, span ID, event type, payload) so you can plug them directly into notebooks or scripts.

The goal is to provide **toy yet realistic structures** that:

* expose trace‑tree divergence,
* show latency gaps,
* demonstrate correction & recovery loops,
* and include a bit of noise for testing heuristics.

No external frameworks are required.

---

## 📂 Files in this directory

### **1. `simple_correction_loop.jsonl`**

A short, readable trace demonstrating:

* an early drift-like wobble,
* a small correction step,
* recovery,
* and continuation.

Useful for:

* validating visualization tools,
* testing divergence calculations,
* stepping through early‑instability signals by hand.

---

### **2. `noisy_mixed_sessions.jsonl`**

A bundle of several short synthetic sessions with:

* mild noise (latency jitter, inconsistent arg shapes),
* occasional divergence between sibling spans,
* mixed outcomes (stable, unstable, recovered, failed).

Useful for:

* testing metrics against multiple sessions at once,
* evaluating heuristic thresholds,
* notebook experiments.

---

### **3. `generate_synthetic_traces.py`**

A flexible generator script that creates:

* deterministic toy traces (easy to read),
* noisy traces with configurable parameters,
* long chains of turns for loop or drift experiments.

You can customize:

* number of sessions,
* noise levels,
* drift / correction frequency,
* span branching shapes,
* latency jitter.

Example usage:

```bash
python generate_synthetic_traces.py --sessions 5 --noise medium > out.jsonl
```

---

## 🔧 JSONL format (minimal schema)

Each line looks like:

```json
{
  "timestamp": "2025-01-01T00:00:01.234Z",
  "trace_id": "abc123def4567890",
  "span_id": "0011223344556677",
  "event_type": "step",
  "payload": { "latency_ms": 85 }
}
```

Fields are intentionally lightweight:

* **timestamp** — ISO8601 with ms precision
* **trace_id** — session‑scoped opaque string
* **span_id** — operation‑scoped opaque string
* **event_type** — one of `step`, `drift_like`, `correction`, `recover`, `end`, etc.
* **payload** — arbitrary small dict (latency, args, notes)

The traces here are **not** intended to match any production schema — they’re teaching artifacts.

---

## 🧪 How to use these traces

### In notebooks

Load a trace into a DataFrame:

```python
import json
lines = [json.loads(l) for l in open("synthetic_traces/simple_correction_loop.jsonl")]
```

Then:

* draw a trace tree,
* compute relative latency gaps,
* plot divergence,
* visualize instability episodes.

### In scripts

Use the CLI helper:

```bash
python scripts/compute_metrics_from_jsonl.py --file synthetic_traces/noisy_mixed_sessions.jsonl
```

---

## 📜 License

These synthetic traces are free to reuse and modify under **CC‑BY‑4.0**. They contain no real data.
