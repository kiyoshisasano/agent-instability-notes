# Shared Definitions for Instability Metrics

This file collects **common terminology, data assumptions, and structural primitives** used across all metric definitions in `metrics/`.

The goal is to avoid repeating the same explanations in every metric document.

---

## 📌 1. What Counts as a "Trace"?

All metrics in this repo assume a **JSONL trace format**:

* One event per line
* Each line is a valid JSON object
* Session-level grouping is done via `trace_id`
* Operation-level grouping is done via `span_id`

Minimal expected fields:

```jsonc
{
  "timestamp": "ISO8601 string",
  "trace_id": "opaque string",
  "span_id": "opaque string",
  "event_type": "string",
  "component": "agent|tool|system|runtime|...",
  "payload": {}
}
```

These traces may come from **Langfuse**, **Arize**, **LangChain**, **LlamaIndex**, hand-written logging, or a fully custom system.

Metrics in this repo avoid binding to any analytics product.

---

## 📌 2. Basic Structural Terminology

### **2.1 Session**

A sequence of events sharing the same `trace_id`.

### **2.2 Span**

A unit of work (tool call, reasoning step, API request). Identified by `span_id`. A span may contain child spans.

### **2.3 Turn**

A high-level interaction cycle, roughly:

* User input
* Agent reasoning
* Tool calls (optional)
* Agent reply

Traces rarely contain an explicit "turn" index, so **many metrics infer turns** based on timestamps or structural patterns.

### **2.4 Step Group (synthetic grouping)**

Some metrics compare spans that are “structurally equivalent”, e.g.:

* Same parent span
* Same tool method
* Same reasoning stage

This repo calls these **step groups**: sets of spans comparable for divergence or latency patterns.

---

## 📌 3. Early Instability Signals (Baseline Vocabulary)

Many metrics rely on the following shared vocabulary:

### **3.1 Micro-divergence**

Small structural mismatches appearing before the system visibly fails.

Examples:

* Slightly different argument shapes
* Extra retry spans
* Latency outliers between sibling spans

### **3.2 Recovery Window**

The portion of a session after an anomaly where we observe whether the system stabilizes.

### **3.3 Correction Attempt**

Any action—model rewrite, tool retry, parameter adjustment—that *appears intended* to realign behavior.

### **3.4 Relapse**

A new anomaly after an apparent correction. Used in metrics like **post-correction relapse rate**.

---

## 📌 4. Assumed Invariants

To keep metrics generic, we assume only these minimal invariants:

### **4.1 Timestamps are monotonic per trace**

Not globally sorted—just non-decreasing for the same session.

### **4.2 Spans form a DAG**

No strict tree requirement. Loops, retries, or external callback structures are allowed.

### **4.3 Event types are descriptive but not standardized**

Metrics rely on:

* structural similarity
* latency
* ordering

Not on any canonical classification.

### **4.4 Correction is inferred, not asserted**

Since traces often lack explicit “repair markers”, inference is based on patterns like:

* parameter correction
* error disappearance
* tool success after repeated failures

---

## 📌 5. Generic Operations Used by Multiple Metrics

These appear repeatedly across metric definitions.

### **5.1 Relative latency**

Always computed as:

```python
abs(a - b) / max(a, b, 1)
```

### **5.2 Structural signature**

Any hashable representation of a span’s structural properties:

* tool name
* method
* argument shape
* response class

Used for divergence metrics.

### **5.3 Drift window detection**

A lightweight heuristic:

* Anomaly detected → mark drift start
* Continue scanning until stabilization event → mark recovery

This pattern underlies several metrics.

### **5.4 Session termination classification**

Used for `session-closure-profile.md`.

Possible buckets:

* Completed
* Interrupted
* Failed
* Abandoned
* Timeout

---

## 📌 6. Metric Design Principles Shared Across This Repo

1. **Framework independence**
   Metrics must work on raw JSONL logs, no SDK required.

2. **Stable under partial traces**
   Missing events should degrade gracefully.

3. **Interpretability over cleverness**
   Simple ratios, deltas, and structural comparisons beat complex ML-based scoring.

4. **Small, composable building blocks**
   Metrics often reuse the primitives defined in this file.

5. **Focus on *instability*, not accuracy**
   These metrics detect *when behavior begins to wobble*, not whether outputs are correct.

---

## 📌 7. When to Extend This File

You should add shared definitions here when:

* multiple metrics repeat the same prose, or
* the concept is general enough to use across examples and notebooks.

Avoid adding system-specific or vendor-specific concepts.

---

If you'd like changes or want to generate the next metric file, just let me know.
