# Trace Tree Divergence

> How small structural mismatches in a trace tree can reveal early signs of workflow drift.

---

## 1. What is trace tree divergence?

A **trace tree** represents how a multi-turn agent breaks down a task into reasoning steps, tool calls, and nested operations. When a system is healthy, sibling spans within similar structural positions tend to be **consistent** in:

* argument structure
* reasoning depth
* ordering
* latency bands
* tool usage patterns

**Trace tree divergence** refers to small structural or statistical mismatches across these spans that appear *before* any visible failure.

This document describes what those divergences look like and how to detect them.

---

## 2. Why divergence matters

Most multi-turn failures begin as tiny inconsistencies:

* one branch of a reasoning step becomes deeper than the others,
* two equivalent tool spans have different signature shapes,
* latency splits in a way that suggests uneven work,
* parallel paths start drifting apart in structure.

These misalignments often happen **several turns before** a true failure or correction. They are among the most reliable early signals of instability.

---

## 3. Typical divergence patterns

Below are common divergence categories observed across many systems.

### 3.1 Signature mismatch

Two spans that "should" be structurally equivalent differ in:

* argument fields
* JSON shapes
* number of keys
* presence/absence of optional metadata

Example indicator:

```json
{
  "span_id": "...",
  "args": {"query": "A"}
}
{
  "span_id": "...",
  "args": {"query": "A", "filters": {"top_k": 5}}
}
```

### 3.2 Depth imbalance

Equivalent branches have different nested depth:

* one path performs multiple inner reasoning steps,
* another path collapses early or shortcuts steps.

This can indicate uneven internal decision-making.

### 3.3 Ordering divergence

Sibling spans execute in reversed or inconsistent order:

* tool → filter → rank vs
* rank → tool → filter

This often correlates with unstable or drifting internal logic.

### 3.4 Latency split

Two parallel spans show a widening gap in latency despite similar work:

```
span A latency = 42 ms
span B latency = 217 ms
```

Latency split is especially important because it often tracks deeper reasoning drift.

---

## 4. How to detect divergence

Detection does *not* require heavy algorithms. A few lightweight checks catch most cases.

### 4.1 Compare signatures of sibling spans

Define a simple signature function:

```python
def signature(span):
    return {
        "tool": span.get("tool"),
        "shape": sorted(span.get("args", {}).keys()),
        "depth": span.get("depth", 0),
    }
```

If siblings have different signatures, you have early divergence.

### 4.2 Relative latency gap

Use the metric defined under `metrics/relative-latency-gap.md` to detect gaps within a group of structurally equivalent spans.

A rising relative gap across turns is a strong early-warning signal.

### 4.3 Structure diff across turns

Track how the signature set for a given subtree changes across turns.
A simple count of mismatches is often enough:

```python
mismatch_count = len(set(signatures)) - 1
```

---

## 5. Visual markers (recommended)

Visualizing divergence is often more intuitive than reading JSON.
A minimal visualization can be:

* a tree diagram with **red nodes** marking signature shifts,
* a latency heatmap across corresponding spans,
* a side-by-side diff of subtree structures,
* "branch width" plots showing how many tool calls occur at each level.

Diagrams make it easier to spot:

* where divergence begins,
* whether it is local or systemic,
* whether it stabilizes or spreads.

---

## 6. Example scenario (simplified)

```
Turn 2  Branches A and B both call search_api with the same schema.
Turn 3  Branch A adds a new filter object; Branch B does not.
Turn 4  Latency gap between A and B increases.
Turn 5  A retries with deeper reasoning; B stays shallow.
Turn 6  Downstream behavior diverges significantly.
```

The earliest detectable signal was the **signature mismatch** at Turn 3.

---

## 7. Divergence vs normal variation

Not every difference is instability. Benign variation includes:

* nondeterministic latency jitter;
* model temperature effects that do not affect structure;
* optional fields that vary but do not affect decision flow;
* harmless reordering when operations are independent.

Divergence becomes concerning when:

* it persists across turns,
* it widens (signature set grows),
* it correlates with other signals (latency gaps, retries, tool failures),
* the system deviates from expected workflow.

---

## 8. Using divergence in your own work

Trace tree divergence is a versatile signal. You can use it to:

* detect early instability episodes,
* drive correction attempts,
* cluster sessions by structural behavior,
* highlight weak spots in tool chains and routing logic.

Combine it with:

* `nested-tool-inconsistency.md` for deeper tool-level patterns,
* `early-instability-signals.md` for broader early-warning cues,
* `metrics/relative-latency-gap.md` to quantify divergence severity.

---

If you notice new divergence shapes in your own traces, consider adding new examples or a new subcategory under `concepts/`.
