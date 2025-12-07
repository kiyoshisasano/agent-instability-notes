# Nested Tool-Call Inconsistency

> How small signature drifts inside multi-hop tool sequences become early warning signals for agent instability.

---

## 1. What this note covers

This document explains **nested tool-call inconsistency** — a structural early-warning signal observed in multi-step agent traces. It is a lightweight, framework-agnostic concept you can apply to any system that emits:

* trace IDs / span IDs
* tool-call attempts and results
* timestamps or latency
* basic argument structures (dicts, lists, strings)

The goal is to show why *very small divergences* across structurally equivalent tool calls often predict downstream failures.

---

## 2. Intuition: where this appears in real systems

Multi-turn agents often execute **tool chains** such as:

```
plan → lookup → filter → refine → act
```

When these chains are stable, their tool calls tend to be:

* similar in shape (keys, argument schema),
* similar in depth (consistent parent/child spans),
* similar in latency profile,
* similar in ordering.

But when instability emerges, these patterns begin to wobble.

Before the model outputs anything obviously incorrect, you often see:

* minor key omissions,
* argument reshaping (list → single value, or vice versa),
* subtle mismatches in numeric ranges,
* inconsistent parameter naming,
* growing variance in hop-to-hop latency.

These inconsistencies are what we call **nested tool-call inconsistency**.

---

## 3. Formal-ish definition (but still accessible)

A *nested tool-call cluster* is defined as:

* all tool-related spans under a shared parent span (same trace),
* with the same `tool` or `operation` label,
* occurring within a short turn-distance window.

A cluster is **inconsistent** when **structurally equivalent calls are not equivalent anymore**, specifically:

### Signs of inconsistency

* **argument drift**: key set mismatch or changed structure
* **signature drift**: hash/shape of the argument tuple changes
* **execution-depth drift**: nested spans change depth unexpectedly
* **latency divergence**: relative latency variance spikes beyond normal
* **ordering drift**: sibling operations appear in a different sequence

These divergences often appear several turns before a visible error.

---

## 4. Why nested inconsistency matters

Nested tool chains behave like *reaction chambers*. If the chain is brittle, tiny deviations can compound:

* inconsistent arguments → inconsistent results
* inconsistent results → unstable reasoning
* unstable reasoning → tool calls with improvised structure
* eventually → visible agent failure or invalid output

This progression is nearly universal across agent designs.

Nested inconsistency is therefore a strong **early instability signal**.

---

## 5. How to detect it from raw traces

You only need:

* tool-call spans
* their arguments
* their parent/child relationships
* their latencies

### 5.1 Argument key comparison

```python
keys = [set(call.args.keys()) for call in cluster]
key_drift = len({frozenset(k) for k in keys}) > 1
```

### 5.2 Argument signature hashing

```python
sig_drift = len({call.signature_hash() for call in cluster}) > 1
```

### 5.3 Relative latency divergence

```python
rel_diffs = []
for a, b in zip(cluster, cluster[1:]):
    rel = abs(a.latency_ms - b.latency_ms) / max(a.latency_ms, b.latency_ms, 1)
    rel_diffs.append(rel)
latency_spike = max(rel_diffs) > 0.25  # heuristic
```

### 5.4 Depth and ordering drift

Compare `span_id` parentage and sequence index.

---

## 6. Visual signature (conceptual diagram)

Stable chain:

```
parent
 ├─ tool_call(args A)
 ├─ tool_call(args A)
 └─ tool_call(args A)
```

Inconsistent chain:

```
parent
 ├─ tool_call(args A)
 ├─ tool_call(args A')   ← tiny drift begins
 ├─ tool_call(args B)    ← new structure
 └─ tool_call(args B, depth+1)  ← divergence worsens
```

This pattern is highly predictive of future drift episodes.

---

## 7. How to interpret inconsistency

### When it *is* a warning

* the agent switches from structured reasoning to improvisation
* tool-call shapes diverge for no semantic reason
* latency deltas grow rapidly
* argument keys fluctuate

### When it is *not necessarily* instability

* the tool is polymorphic by design
* arguments reflect genuine user branching
* external APIs cause natural variance

Context matters — but **unexpected incoherence inside a stable chain** nearly always correlates with future problems.

---

## 8. Summary

Nested tool-call inconsistency is a simple yet powerful concept:

* it requires no model introspection,
* it can be computed from raw JSONL logs,
* it surfaces instability earlier than output-level evaluation,
* and it generalizes across frameworks.

Use this pattern alongside:

* **trace-tree divergence**
* **relative latency gaps**
* **recovery turn-distance**

…to build a clearer map of how and when multi-turn agents begin to drift.

---

*End of document.*
