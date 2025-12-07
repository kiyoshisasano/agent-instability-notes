# Early Instability Signals

> Practical, framework‑agnostic clues that an agent is beginning to drift long before a visible failure.

---

## 🎯 What this note covers

This document introduces **"early instability signals"** — subtle, structural irregularities in multi‑turn agent behavior that often appear **several steps before** an error becomes obvious.

The goal is to provide:

* simple, framework‑independent terminology,
* signals that can be computed from traces alone,
* intuition for *where* instabilities tend to show up first.

These signals complement (but do not depend on) any specific agent framework, orchestration layer, or governance model.

---

## 1. Why early instability matters

Most multi‑turn failures are not sudden. They build up:

* a small mismatch in parameters,
* slightly divergent tool‑call structure,
* subtle latency rhythm shifts,
* inconsistent state or memory references.

Individually, these deviations may look harmless.
Together, they often signal **the beginning of a longer drift episode**.

Early signals help you:

* catch problems before user‑visible mistakes occur,
* identify regression points when upgrading models,
* compare behavior across agents and workflows,
* reason about long‑horizon stability.

---

## 2. Categories of early signals

Most early signals fall into three broad families: **structural**, **temporal**, and **semantic-light**.

### 2.1 Structural signals (shape‑based)

These arise from the *shape* of the trace tree or tool sequence — not from content.

Representative patterns:

* **Trace tree divergence**
  Siblings that should be structurally symmetric begin to diverge in depth, span count, or ordering.

* **Nested tool-call inconsistency**
  Multi-step tool flows evolve different argument signatures, method sequences, or branching.

* **Checkpoint misalignment**
  Turn boundaries or state checkpoints appear out of expected order.

Structural signals are especially valuable because they rarely require domain knowledge.

### 2.2 Temporal signals (timing‑based)

These rely on *relative changes*, not absolute latency.

Examples:

* **Relative latency gaps** across structurally similar spans.
* **Timing rhythm shifts** within a tool chain (predictable → irregular).
* **Turn‑distance inflation** — the system requires more steps to complete an otherwise standard workflow.

Temporal signals flag instability early because timing often reflects internal uncertainty or repeated correction attempts.

### 2.3 Semantic‑light signals

These use minimal content analysis — enough to spot inconsistencies, but without heavy NLP.

Examples:

* **Inconsistent argument sets** between steps.
* **Rewriting of constraints** across turns.
* **Soft contradictions** (e.g., self-cancellation, unintended relaxing of criteria).

These are useful when full semantic drift detection is too expensive or unnecessary.

---

## 3. Typical early‑instability timeline

In many real systems, early signals follow this rough sequence:

1. **Temporal anomaly**
   Relative latency or rhythm shifts.
2. **Structural irregularity**
   Divergence in span counts, tool signatures, or subtree shapes.
3. **Semantic-light mismatch**
   Arguments or constraints drift.
4. **Visible failure**
   The user finally notices.

Catching the top two layers early provides significant observability headroom.

---

## 4. Practical extraction from JSONL traces

Early signals can be computed from simple fields:

* `trace_id`
* `span_id`
* timestamps
* tool call payloads
* structural order of spans

Minimal example logic (pseudocode):

```python
# Relative latency gap
(lat_a, lat_b) = (span_a.lat_ms, span_b.lat_ms)
relative_gap = abs(lat_a - lat_b) / max(lat_a, lat_b, 1)
```

```python
# Structural divergence (hash-based)
signatures = [hash(serialize(span.payload.get("args", {}))) for span in siblings]
divergence = len(set(signatures)) - 1
```

```python
# Argument drift across turns
if normalize(args[t]) != normalize(args[t-1]):
    flag("arg_inconsistency")
```

These heuristics intentionally avoid heavy modeling — the goal is **detectability**, not perfect diagnosis.

---

## 5. When these signals shine

Early instability signals are most useful when:

* workflows involve **multiple hops** or **tool chains**,
* agents rely on **intermediate reasoning** or planning,
* latency budgets are tight and deviations matter,
* you want early warnings without deep semantic checks.

They are less useful for:

* single-turn Q&A,
* purely deterministic scripts,
* cases where all tool calls are always identical.

---

## 6. Summary

Early instability signals let you:

* observe drift before it becomes failure,
* reason about long-horizon behavior from traces alone,
* track how corrections propagate through a workflow,
* compare stability across models, versions, or orchestrators.

These signals form the foundation for the metrics, notebooks, and examples in the rest of this repository.
