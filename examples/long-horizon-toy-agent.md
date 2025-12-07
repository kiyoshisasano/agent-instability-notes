# Long-Horizon Toy Agent

> A small, synthetic agent scenario designed to surface **slow instability drift** across 20–40 turns.

This example is intentionally lightweight and framework-agnostic.
Its purpose is to show how **tiny, early deviations** accumulate into visible behavioral wobble over longer sessions.

---

## 🎯 Why this example exists

Real multi-turn agents rarely fail immediately.
More often:

* the first few turns look healthy,
* slight divergence appears around turns 5–10,
* correction attempts briefly stabilize behavior,
* then the session degrades again in turns 15–25.

This pattern is extremely common in planning agents, retrieval-based flows, or tool-heavy orchestrators.

This toy agent simulates exactly that progression.

---

## 📐 Scenario structure

The agent has:

* a **simple goal**: replicate a 3‑step reasoning pattern,
* a **soft memory module**: stores recent outputs but with mild entropy,
* a **tool stub**: returns pseudo-random latencies and occasional partial failures,
* a **loop of 20–40 turns**, with each turn producing a short trace.

Nothing about this agent is realistic on its own — but the *shape* of the behavior is.

---

## 🧪 Instability phenomena you can observe

This example reliably produces:

### 1. **Latency drift within the same reasoning step**

Even when content is stable, step-level execution latency slowly diverges.
This enables testing of:

* **relative latency gaps**,
* **micro-spikes**, and
* “slow warmup → sudden wobble” curves.

### 2. **Trace-tree divergence**

Around turns 8–12:

* sibling spans begin to disagree,
* small structural mismatches appear,
* signature hashes begin to differ.

### 3. **Miniature correction loops**

At random intervals:

* the agent’s output fails basic internal checks,
* a “soft correction” re-stabilizes the next 1–3 turns,
* drift returns later.

This is useful for testing **post-correction relapse rate**.

### 4. **Outcome variability**

Depending on random factors:

* some sessions close cleanly,
* others loop,
* others terminate early.

This variability is helpful for **session closure profile** analysis.

---

## 🧵 Example pseudo-trace (simplified)

Below is a very small illustrative sample (not canonical PLD, purely narrative):

```jsonc
{"turn": 7, "span": "reason-step", "latency_ms": 128, "content": "Plan step looks good"}
{"turn": 8, "span": "reason-step", "latency_ms": 199, "content": "Slight mismatch in recall"}
{"turn": 9, "span": "reason-step", "latency_ms": 214, "content": "Signature drift detected (internal)"}
{"turn": 10, "span": "self-check", "status": "correction"}
{"turn": 11, "span": "reason-step", "latency_ms": 137, "content": "Stabilized"}
{"turn": 17, "span": "reason-step", "latency_ms": 248, "content": "Diverging again"}
```

This example is intentionally non-deterministic to ensure that each run produces slightly different long-horizon shapes.

---

## 🧰 How to run the toy agent

The toy agent can be implemented in ~40 lines of Python.
A minimal implementation is provided in:

```
examples/synthetic_traces/generate_synthetic_traces.py
```

Run it like this:

```bash
python examples/synthetic_traces/generate_synthetic_traces.py \
  --variant long_horizon \
  --turns 30 \
  > long_horizon_trace.jsonl
```

Replace `--turns` with 20–50 depending on the instability duration you want to observe.

---

## 📊 What to do with the output

Once you generate `long_horizon_trace.jsonl`, try these steps:

1. **Inspect trace-tree structure**

   * `examples/notebooks/01_inspect_trace_tree.ipynb`

2. **Compute early-instability metrics**

   * `examples/notebooks/02_early_instability_metrics.ipynb`

3. **Plot divergence paths**

   * `examples/notebooks/03_visualize_trace_divergence.ipynb`

4. **Run CLI metrics over it**

   ```bash
   python scripts/compute_metrics_from_jsonl.py --file long_horizon_trace.jsonl
   ```

---

## 📝 Takeaways

This scenario is ideal for studying:

* how minor early deviations become major late-stage instability,
* how correction loops temporarily mask deeper drift,
* how latency drift and structural divergence interact,
* how long-horizon behavior reveals underlying design weaknesses.

Use it as a sandbox to calibrate your intuition before analyzing larger or production-grade logs.
