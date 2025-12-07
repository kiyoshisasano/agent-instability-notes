# Correction and Recovery Loop

> How multi‑turn agents move from “something feels off” → “back on track”, using only traces, structure, and lightweight checks.

---

## 1. Why correction loops matter

In many multi‑turn agents, visible failure rarely appears suddenly. Instead, behavior drifts a few steps before the system produces an obviously incorrect or unstable output.

This file describes **how to reason about correction loops** using only:

* structural trace inspection,
* latency and pacing signals,
* tool‑call patterns,
* simple turn‑to‑turn comparisons.

No specific framework or runtime is assumed.

---

## 2. The minimal loop shape

Most correction cycles, regardless of tooling or framework, follow a recognizable structural pattern:

```
initial_drift
    ↓
correction_attempt
    ↓
recovery_check
    ↓
return_to_flow  (or relapse)
```

We do not assign formal phases—this repo uses **plain, framework‑agnostic language**—but the shape is consistent across many observed systems.

---

## 3. Detecting the *initial drift*

Early drift is often subtle. Common markers include:

### 3.1 Content‑level shifts

* missing or relaxed constraints
* partial instruction misunderstanding
* logically inconsistent intermediate steps

### 3.2 Structural shifts

* mismatches between parallel branches in a trace tree
* reordering of tool‑call sequences
* sudden changes in reasoning depth

### 3.3 Latency / pacing signals

* spikes within a group of structurally similar spans
* unusually fast (truncated) outputs
* multi‑step latency decoupling

Any of these may signal that the workflow is beginning to diverge.

---

## 4. What counts as a “correction attempt”

A correction attempt is any behavior that tries to bring the agent back into alignment, such as:

* internal self‑correction in model reasoning
* a more explicit or constrained tool call
* a user‑prompt‑driven clarification
* a fallback policy or template
* retrying an operation with stricter parameters

In practice, correction attempts are visible through:

* **signature adjustments** (arguments, schemas, formats)
* **additional validation turns**
* **retries with modified strategy**
* **narrowing of the search space**

---

## 5. Recovery checks: “Is the system healthy again?”

After an attempted correction, the system typically performs some implicit or explicit recovery check. Examples:

### 5.1 Structural sanity checks

* tool outputs regain consistent shape
* trace tree branches realign
* missing constraints reappear naturally

### 5.2 Behavioral checks

* reasoning depth returns to normal
* looping behavior ceases
* pacing stabilizes

### 5.3 User‑confirmation or goal restatement

Not always required, but often helpful:

> “Just to confirm, continuing with the adjusted parameters…”

Recovery is best interpreted as **convergence toward the expected workflow**, not perfection.

---

## 6. Return to flow — or relapse

A session may return to normal flow when:

* structural mismatches shrink or disappear
* tool‑call sequences behave predictably
* latency patterns stabilize
* no further corrections are implicitly attempted

A **relapse** occurs when:

* drift reappears shortly after correction
* the system oscillates between partial fixes and new deviations
* the session repeatedly alternates between divergence → correction → partial recovery

Relapse detection is the basis for metrics like **post‑correction relapse rate** (defined under `metrics/`).

---

## 7. What you can measure

Many instability‑oriented metrics can be expressed in terms of this loop:

* **time‑to‑correction** (from first drift marker to first correction attempt)
* **recovery turn distance** (turns between correction and stable flow)
* **relapse rate** (how often drift returns after a correction)
* **correction frequency** (number of corrections per session)

These can all be derived from JSONL traces with minimal assumptions.

---

## 8. A small example sketch

A simple correction loop may look like:

```
Turn 3   Slight divergence in two sibling tool spans
Turn 4   Latency gap spikes across equivalent spans
Turn 5   Agent retries the tool with a more constrained set of arguments
Turn 6   Outputs realign; latency normalizes
Turn 7   Flow continues normally
```

From this trace, you could compute:

* `time_to_correction = 5 - 3 = 2 turns`
* `recovery_turn_distance = 7 - 5 = 2 turns`

---

## 9. How to use this document

Use this file together with:

* `concepts/early-instability-signals.md` — for the earliest detectable hints
* `concepts/trace-tree-divergence.md` — for structure‑based drift cues
* `metrics/recovery-turn-distance.md` — for quantifying how long recovery takes
* `metrics/post-correction-relapse-rate.md` — for measuring relapse patterns

This conceptual loop ties together the rest of the repo’s definitions and examples.

---

If you observe new loop shapes or mixed patterns in your own traces, consider adding:

* new example files under `examples/`
* new instability categories under `concepts/`
* new metrics capturing behaviors you find significant.

This repo is meant to grow with real usage and field insights.
