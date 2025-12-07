# Recovery Turn Distance

> A simple, trace‑only estimator of how long it takes an agent to return to stable behavior after an instability episode.

---

## 1. What this metric measures

**Recovery Turn Distance (RTD)** measures:

> **How many turns occur between the *onset of instability* and the first reliable sign of *behavioral recovery*.**

It is a *turn-based* metric (not time-based). This keeps the metric portable across systems with different latency characteristics.

RTD helps answer questions like:

* "After the agent wobbles, how fast does it stabilize again?"
* "Does the system recover quickly or drift for several turns?"
* "Are my correction mechanisms effective?"

This is useful for long-horizon or tool-using agents where instability may appear subtly in early steps before becoming visible.

---

## 2. When to use

Use RTD when:

* you have **multi-turn traces** with identifiable turns,
* your system occasionally enters **unstable or ambiguous states**,
* you want **lightweight early-warning analytics** without full-blown instrumentation.

RTD does *not* require PLD semantics or formal labeling. It only assumes:

* a consistent `turn_index` or equivalent ordering,
* a boolean or heuristic flag indicating whether a turn is **unstable**,
* a heuristic or signal that a turn is **stable again**.

---

## 3. Required trace fields

You only need lightweight structure:

```json
{
  "trace_id": "...",
  "turn_index": 7,
  "signals": {
    "instability": true | false,
    "recovered": true | false
  }
}
```

Minimal signals used:

* `instability = true` → marks the *start* of an instability episode
* `recovered = true` → marks the *end* of that episode

Anything that approximates these conditions works:

* drift detector flags
* constraint-mismatch scores
* large latency gaps
* divergence alerts
* tool-call inconsistencies
* ad-hoc heuristics (provided in examples)

---

## 4. How to compute RTD

### 4.1 Definition

```text
RTD = (turn_index at recovery) − (turn_index at instability onset)
```

### 4.2 Pseudocode

```python
def recovery_turn_distance(events):
    onset = None
    distances = []

    for e in events:
        if e.signals.instability and onset is None:
            onset = e.turn_index

        elif e.signals.recovered and onset is not None:
            distances.append(e.turn_index - onset)
            onset = None

    return distances
```

### 4.3 Multiple episodes per trace

A single trace may have several instability episodes:

```
Turn 4: instability
Turn 7: recovered → RTD = 3
Turn 15: instability
Turn 18: recovered → RTD = 3
```

You compute RTD per episode.

---

## 5. Practical heuristics

### 5.1 How to detect instability onset

Choose any condition appropriate for your system:

* tool-call retry loops
* divergence between similar branches
* sudden relative-latency spikes
* schema inconsistencies
* missing arguments
* conflicting intermediate reasoning

### 5.2 How to detect recovery

Recovery signals often include:

* return to consistent structure
* simple, low-entropy responses
* normalized tool signatures
* stable latency relative to prior turns

You can also use a rolling window heuristic:

```
recovered = (no instability signals in last 2–3 turns)
```

---

## 6. Interpretation

### Low RTD (0–2 turns)

* System recovers quickly
* Correction loop is effective
* Early drift does not propagate

### Medium RTD (3–6 turns)

* System wobbles before stabilizing
* Recovery may depend on context or heuristics

### High RTD (7+ turns)

* Drift propagates across many steps
* Possible planning instability or looping
* Indicates need for stronger correction or guardrails

---

## 7. Example

```
turn 3: latency spike → instability
turn 4: inconsistent tool args
turn 5: correction attempt
turn 6: stable structure → recovered
```

RTD = 6 − 3 = **3 turns**

---

## 8. Caveats

* RTD is **turn-based**, not time-based – good for structural analysis but blind to wall-clock delays.
* Recovery may be ambiguous in noisy traces.
* Heuristics must be adapted to your agent type (planner vs reactive vs tool-heavy).
* Multiple concurrent instability dimensions may require multi-signal fusion.

---

## 9. Summary

**Recovery Turn Distance** is a simple, framework-free metric for evaluating how long an agent remains unstable after an issue first appears.

It helps uncover:

* how resilient your agent is,
* how well correction mechanisms work,
* where long-horizon degradation starts.

This metric is intentionally lightweight and works out-of-the-box with JSONL traces and simple Python scripts.

---

*Next file suggestion: `post-correction-relapse-rate.md` or `failover-frequency.md`.*
