# Tool-Chain Instability

> How multi-step tool sequences degrade, drift, or silently break across long-horizon agent workflows.

---

## 1. Overview

Tool-chain instability refers to **structural degradation across multi-step tool sequences** in an agent workflow.

Unlike single-call failures, these patterns emerge only when:

* tools are **chained** (A → B → C),
* the agent uses **derived inputs** from earlier results,
* latency, schema, or semantic mismatches **accumulate slowly**, and
* the agent keeps going until a visible failure occurs.

This document provides a compact set of illustrative examples and templates to reason about these breakdown modes.

---

## 2. Why tool-chain instability matters

Multi-tool workflows often act as **amplifiers**:

* A small deviation in tool A becomes a larger deviation in tool B.
* Latency spikes propagate through later calls.
* Schema mismatches accumulate.
* Partial failures amplify semantic drift.

Early detection helps prevent costly cascading failures.

---

## 3. Minimal assumptions

We make **no framework assumptions**. A "tool" may be:

* an API call
* a retrieval step
* a structured RAG query
* an embedding similarity lookup
* a code execution step

The only things assumed:

* you have JSONL traces with timestamps
* each tool call has args, result, and latency
* spans can be structurally grouped

---

## 4. Instability pattern 1: Schema creep

**Symptom:** The structure of results from upstream tools gradually changes.

### Example

```
Step A returns:
  {"name": "alice", "age": 31}

Step B expects:
  {"name": str, "age": int}

But Step A (later in the session) returns:
  {"person": {"name": "alice", "age": 31}}
```

Now B must adapt on the fly. Some LLMs do, some fail silently.

### Detection heuristic

* Compare **key sets** across tool-call siblings.
* Flag sessions where **key-set similarity** drops.

---

## 5. Instability pattern 2: Argument drift

**Symptom:** Downstream tool arguments begin diverging from upstream intent.

### Example scenario

* User wants hotels with *wifi + parking*.
* Tool sequence:

  * A = constraint extraction
  * B = candidate fetch
  * C = ranking

If A outputs: `{wifi=True, parking=True}`
but B receives: `{wifi=True}`,
that drift tends to propagate to C.

### Detection heuristic

* Compute **argument similarity** between adjacent tool calls.
* Track divergence episodes as sessions progress.

---

## 6. Instability pattern 3: Latency propagation

**Symptom:** A delay early in the tool chain inflates later latencies.

### Example

```
Call A latency: 80ms
Call B latency: 420ms
Call C latency: 980ms
```

A spike in C may reflect **compounding error-handling**, not slow hardware.

### Detection heuristic

* Track **relative latency gap** between siblings.
* Prefer normalizing by median/expected latency.

---

## 7. Instability pattern 4: Partial-failure cascade

**Symptom:** A tool returns partial data (missing fields, empty lists), and the agent continues anyway.

### Example

```
A returns: { results: [] }   # expected non-empty
B attempts ranking on empty list → fallback mode
C attempts synthesis → low-quality output
```

By the time C fails, the root cause was already visible in A.

### Detection heuristic

* Mark tool returns that violate expected invariants.
* Trace how long the session continues after such events.

---

## 8. Instability pattern 5: Mixed-schema outputs

Some tools return a structured JSON object most of the time, but fall back to an unstructured natural-language blob on rare failures.

### Detection heuristic

* Detect transitions between structured and unstructured payloads.
* Flag sessions where this occurs mid-chain.

---

## 9. Basic analysis snippet

```python
import json
from collections import defaultdict

def tool_chain_segments(events):
    chains = defaultdict(list)
    for ev in events:
        if ev.get("component") == "tool":
            chains[ev["trace_id"]].append(ev)
    return chains

# Example usage: identify argument drift
for trace_id, chain in tool_chain_segments(events).items():
    for a, b in zip(chain, chain[1:]):
        if a["payload"]["args"] != b["payload"]["args"]:
            print(trace_id, "argument drift detected")
```

This is intentionally minimal—adapt it to your trace format.

---

## 10. How to use this document

Use this as a **shape dictionary**:

* identify similar patterns in your own traces,
* extend metrics under `metrics/`,
* use notebooks to inspect real sessions.

The goal is not to prescribe a framework, but to provide the vocabulary and structural heuristics for understanding **tool-chain degradation** as it unfolds.

---
