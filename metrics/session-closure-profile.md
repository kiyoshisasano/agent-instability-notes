# Session Closure Profile

## 1. Overview

The **Session Closure Profile** describes *how multi-turn agent sessions actually end*.
Rather than treating all endings as equivalent, this metric breaks closure into meaningful categories that highlight health, abandonment, instability, and forced termination patterns.

This is one of the most actionable, operator-facing instability indicators. Many real failures do **not** appear as explicit errors — they appear as *how a session ends*.

---

## 2. Why This Matters

Multi-turn agents often degrade gradually. The clearest signal of instability is not a single drift event, but the **shape of the session ending**:

* Did the user abandon the session after oscillation?
* Did the agent reach a stable end state?
* Did the system force-terminate due to error buildup?
* Did it prematurely stop despite the task not being complete?

Tracking these closure categories helps teams reason about long-horizon behavior and identify instability patterns that normal evaluation misses.

---

## 3. Closure Categories (Plain-Language)

Each session is assigned exactly one category:

### **1) Natural Completion**

Agent produced an appropriate final answer; user did not continue.

### **2) User Abandonment**

User stopped interacting mid-way.
Common in sessions where instability accumulates subtly.

### **3) Forced Stop (System Halt)**

Runtime terminated the session:

* safety thresholds
* max retries
* error accumulation
* guardrails

### **4) Premature Termination**

Agent stopped early *even though the task was not complete*.
Often associated with:

* looping attempts
* insufficient repair
* loss of state

### **5) Tool-Chain Failure Closure**

A tool or external system created a terminal error causing session stop.

### **6) Correction-Loop Exhaustion**

Session ended because corrections could not stabilize behavior.

These categories are intentionally **framework-agnostic** and derived purely from trace patterns.

---

## 4. How to Infer Closure from Traces

You can classify closures directly from JSONL logs using simple heuristics.

### Example structural signals

* **Last event is user → no further agent response** → *user abandonment*
* **Repeated corrections followed by a stop** → *correction-loop exhaustion*
* **System error events → session_closed** → *forced stop*
* **Tool error just before final event** → *tool-chain failure closure*
* **Stable agent output followed by no continuation** → *natural completion*

---

## 5. Minimal Pseudocode

```python
def classify_session(events):
    last = events[-1]

    if last.component == "agent" and last.event_type == "final_answer":
        return "natural_completion"

    if any(e.event_type == "system_error" for e in events):
        return "forced_stop"

    if any(e.event_type == "tool_error" for e in events):
        return "tool_chain_failure"

    if pattern_of_repair_exhaustion(events):
        return "correction_loop_exhaustion"

    if last.component == "user":
        return "user_abandonment"

    return "premature_termination"
```

---

## 6. When This Metric Is Useful

### 📌 **Best for:**

* long-horizon agents
* tool-calling workflows
* evaluation pipelines
* debugging instability clusters

### ⚠️ **Less useful for:**

* single-turn Q&A
* stateless retrieval tasks

---

## 7. Visualization Idea

A simple but powerful dashboard chart:

```
Session count (Y)
│        ███ forced stops
│   ████ ███ tool failures
│ ██████ ███ user abandonment
│ ██████ ███ natural completions
└──────────────────────────────→ time
```

This immediately reveals whether instability is rising.

---

## 8. Summary

**Session Closure Profile** is a lightweight, framework-free view into how agent workflows *actually end*.
It reveals:

* hidden instability patterns,
* error amplification,
* recovery failures,
* user friction points.

Use it alongside metrics such as:

* **Relative Latency Gap**
* **Recovery Turn Distance**
* **Post-Correction Relapse Rate**
* **Failover Frequency**

Together, these form a coherent early-instability analysis toolkit.
