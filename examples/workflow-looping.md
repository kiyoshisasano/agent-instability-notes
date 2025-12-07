# Workflow Looping

> How multi-turn agent workflows enter unintended loops — and how to detect the early signals before they become runaway cycles.

---

## 1. Overview

Workflow looping happens when an agent repeatedly cycles through a sequence of steps **without making meaningful forward progress**.

This differs from simple repetition or retry logic — looping is an **emergent failure mode** caused by:

* degraded internal state,
* drifting tool-output interpretations,
* repeated partial failures,
* unstable correction attempts,
* or misaligned recovery logic.

This document provides a compact overview of looping patterns and practical ways to detect them from traces.

---

## 2. Why looping appears in multi-turn systems

Multi-turn agents often operate under conditions that make loops easy to trigger:

* LLMs attempting self-correction generate similar but not identical reasoning.
* Tool calls return partial or noisy data.
* Recovery steps temporarily stabilize the agent but do not fully resolve drift.
* Controllers rely on heuristics that degrade over long horizons.

The result: the workflow enters a **near-stationary cycle**.

---

## 3. Minimal assumptions

We make no assumptions about the orchestration framework.

A "workflow step" can be:

* an LLM reasoning span,
* a tool call,
* a retriever query,
* a chain element in LangChain/LangGraph,
* or any logged operational unit.

The only requirements:

* events have timestamps,
* events belong to traces,
* and spans provide minimal structure (IDs, parents, or sequence numbers).

---

## 4. Looping pattern 1: Correction oscillation

**Symptom:** The agent alternates between two states:

```
fix → fail → fix → fail → …
```

Often caused by:

* unstable correction prompts,
* persistent missing fields,
* misinterpreted tool results.

### Detection heuristics

* Count **alternating event types** (e.g., correction → drift → correction).
* Flag sequences where oscillation lasts more than *N* cycles.

---

## 5. Looping pattern 2: Latency plateau cycles

**Symptom:** A repeating sub-workflow with very similar latency signatures.

Example:

```
turn 18: 950ms
turn 19: 960ms
turn 20: 947ms
turn 21: 955ms
```

Rather than progressing, the system repeatedly executes the same expensive step.

### Detection heuristics

* Use **relative latency gap** across sequential spans.
* Identify cycles with low variance and high repetition count.

---

## 6. Looping pattern 3: Argument recurrence

**Symptom:** Tool or function calls repeatedly receive the **same arguments**.

Example:

```
search({query: "cheapest hotels", city: "tokyo"})
search({query: "cheapest hotels", city: "tokyo"})
search({query: "cheapest hotels", city: "tokyo"})
```

This is often a sign that the agent is stuck regenerating the same plan.

### Detection heuristics

* Hash tool arguments.
* Flag spans where the same hash repeats X times.

---

## 7. Looping pattern 4: Incomplete-state reuse

**Symptom:** The agent uses **partial or stale internal state** to regenerate similar reasoning.

This usually occurs after a half-successful repair.

### Detection heuristics

* Look for repeated **sub-trees** of reasoning spans.
* Identify LLM spans with near-identical token patterns or structure.

---

## 8. Example minimal detector

```python
def detect_loops(events, window=4):
    recent = []
    loops = []

    for ev in events:
        sig = (ev.get("event_type"), str(ev.get("payload")))
        recent.append(sig)
        if len(recent) > window:
            recent.pop(0)
        
        # Naive cycle detection
        if len(set(recent)) <= 2 and len(recent) == window:
            loops.append((ev["trace_id"], ev["span_id"]))
    return loops
```

This is intentionally simple. Your production data will benefit from:

* argument hashing,
* clustering similar LLM spans,
* comparing tree shapes.

---

## 9. How looping interacts with instability metrics

Looping is strongly associated with:

* **Post-correction relapse** — a correction appears to work, then the system falls back into the same loop.
* **Recovery-turn distance** — loops inflate the time required to return to a healthy state.
* **Session-closure profile** — looping often ends with forced termination or timeouts.

Cross-referencing these metrics provides a more complete picture.

---

## 10. How to use this document

Use it to:

* identify looping signatures in your own traces,
* extend instability metrics under `metrics/`,
* build small detectors in `scripts/` or notebooks.

The objective is not to eliminate loops entirely — some loops are part of normal retries — but to understand when they become **pathological**.

---
