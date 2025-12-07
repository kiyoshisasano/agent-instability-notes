# Metric: Relative Latency Gap

> **Goal:** Identify early instability by comparing the latency of structurally similar spans (turns, tool calls, or reasoning steps) within the same session.

---

## 1. What this metric captures

The **Relative Latency Gap (RLG)** highlights when a multi-turn agent suddenly takes *much longer* (or unexpectedly shorter) to perform an equivalent operation.

This often precedes visible instability:

* early signs of **reasoning hesitation**,
* silent internal retries,
* divergence in tool-call planning,
* hidden correction attempts,
* unexpected model–model transitions.

RLG is a **simple, trace-only signal**:

* *no model internals required*,
* *no framework coupling*,
* computed only from: `timestamp`, `trace_id`, `span_id`, `execution_stage`.

---

## 2. When RLG is useful

Use this metric when:

* comparing “parallel” tool attempts across turns,
* monitoring stability of repetitive tasks (e.g., structured planning loops),
* inspecting whether correction loops cause silent latency inflation,
* detecting early warning signs before semantic drift becomes visible.

Not useful when:

* a session has only one tool call or one reasoning span,
* latency is dominated by external IO variance (e.g., unstable upstream API).

---

## 3. Core definition

### 3.1 Per-span latency

For any span with timestamps:

```text
t_start, t_end
latency = t_end - t_start
```

You may extract this from JSONL via either:

* explicit `latency_ms` field, or
* computing difference between consecutive events with same `span_id`.

### 3.2 The relative gap

Given two comparable spans, A and B:

```text
RLG(A, B) = | latency(A) - latency(B) | / max(latency(A), latency(B))
```

This yields a normalized value in `[0, 1]`.

* `0` → identical latency
* `~0.1–0.3` → mild variation
* `>0.5` → large deviation (often instability)

### 3.3 Session-level aggregation

For all comparable span pairs in a session:

* `max_RLG` → most extreme divergence
* `mean_RLG` → overall smoothness
* `std_RLG` → volatility indicator

---

## 4. How to choose comparable spans

The metric assumes you can group spans by lightweight structural heuristics such as:

* same `execution_stage` (`processing`, `execution`, `recovery`),
* same tool/method (`hotel_search_api.search`),
* same reasoning class (`thought`, `plan`, `validate`).

**You do not need a strict schema**.

A minimal heuristic is often enough:

```python
group_key = (event.component, event.execution_stage)
```

Then compute RLG across consecutive spans within each group.

---

## 5. Example (small synthetic session)

| Span | Stage      | Latency (ms) |
| ---- | ---------- | ------------ |
| S1   | processing | 128          |
| S2   | processing | 131          |
| S3   | processing | 412          |

Pairs:

* RLG(S1, S2) = |128−131| / 131 = 0.023 → stable
* RLG(S2, S3) = |131−412| / 412 ≈ 0.68 → **instability likely**

---

## 6. Interpreting RLG

### High values (> 0.5) often indicate:

* the agent entered an unexpected branch,
* hidden correction loops or retries,
* model output hesitation or mode-switching,
* upstream tool saturation/slowdowns,
* sudden reasoning chain expansion.

### Medium values (0.2–0.5) may signal:

* growing complexity,
* marginal misalignment accumulating silently,
* transition toward a correction phase.

### Low values (< 0.2) usually mean:

* stable behavior,
* predictable execution patterns,
* consistent planning.

---

## 7. Simple Python reference implementation

```python
import pandas as pd

# df: loaded JSONL with fields [trace_id, span_id, execution_stage, latency_ms]

def compute_rlg(df):
    results = []

    # group by comparable spans
    for key, group in df.groupby(["trace_id", "component", "execution_stage"]):
        latencies = group["latency_ms"].dropna().tolist()
        if len(latencies) < 2:
            continue

        for a, b in zip(latencies, latencies[1:]):
            rlg = abs(a - b) / max(a, b)
            results.append({
                "group": key,
                "latency_a": a,
                "latency_b": b,
                "rlg": rlg,
            })

    return pd.DataFrame(results)
```

---

## 8. Caveats

* Ignore spans dominated by external API variability unless you control the backend.
* Do not mix spans from different tools or fundamentally different operations.
* RLG only becomes meaningful with **multiple** comparable spans.
* Treat high values as **signals**, not errors — RLG is diagnostic, not prescriptive.

---

## 9. Summary

**Relative Latency Gap** is a lightweight, highly general metric for detecting early instability in multi-turn agents.

It works best when:

* applied within sessions,
* grouped by lightweight structural heuristics,
* interpreted as “shape changes” in agent behavior.

It is framework-agnostic and pairs well with:

* recovery-turn-distance,
* post-correction-relapse-rate,
* trace-tree-divergence visualizations.

Use RLG as one of the first signals when inspecting noisy or drifting sessions.
