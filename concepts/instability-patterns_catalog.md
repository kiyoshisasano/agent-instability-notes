# Instability Patterns Catalog

> A practical catalog of early-stage instability patterns observed in multi-turn agents.
> All patterns use **framework-agnostic, citizen-language terms** and rely only on trace structure, latency, and simple span relationships.

---

## 1. Purpose of This Catalog

This catalog provides a shared vocabulary for describing **micro-instabilities** in multi-turn agents.
These patterns are intentionally **implementation-neutral**, **runtime-agnostic**, and **observable from traces alone**.

The goal is to help practitioners:

* diagnose issues *before* visible failures,
* compare traces consistently across frameworks,
* communicate instability signatures without relying on internal lifecycle terminology.

---

## 2. Pattern Categories

All patterns fall into three broad categories:

1. **Structural Instability** – the shape or branching of the trace shifts unexpectedly.
2. **Execution Instability** – the timing, pacing, or consistency of operations fluctuates abnormally.
3. **Semantic Instability** – tool arguments, step outputs, or intermediate reasoning begin diverging from earlier, near-duplicate spans.

Each catalog entry includes:

* **Definition**
* **How to detect it (trace-only)**
* **Why it matters**
* **Where it usually shows up (Langfuse, Arize, LangChain, LlamaIndex usage)**

---

# 3. Structural Instability Patterns

## 3.1 Trace Tree Divergence (Early Structural Drift)

**Definition**
Sibling spans with the same role or intent begin to differ in structure, parameterization, or duration.

**How to detect**

* Compare sibling spans in the trace tree.
* Hash their signatures (arguments, metadata, tool type, step name).
* Divergence score = number of distinct signatures.

**Why it matters**
This is often the **earliest warning signal** that high-level behavior will drift several steps later.

**Common triggers**

* Retry loops with subtle parameter changes
* Non-deterministic reasoning paths
* Tool wrappers that introduce minor shape inconsistencies

---

## 3.2 Runaway Branching

**Definition**
A trace tree that should remain linear suddenly grows parallel sub-branches.

**How to detect**

* Count the number of children per node.
* Compare against expected workflow shape.

**Why it matters**
Indicates that the model is **hedging**, exploring multiple paths, or accidentally duplicating operations.

**Typical contexts**

* Planner-based agents
* Long-horizon evaluators
* Multi-tool orchestrators

---

## 3.3 Collapsing Structure

**Definition**
A workflow that normally branches begins collapsing into single steps, bypassing validations or tool calls.

**How to detect**

* Expected nodes missing.
* Fewer children than in reference structure.

**Why it matters**
Often a sign of:

* silent failure inside reasoning, or
* opportunistic “fast exit” behavior that reduces reliability.

---

# 4. Execution Instability Patterns

## 4.1 Relative Latency Spikes

**Definition**
Two spans that should have similar latency suddenly diverge.

**How to detect**

* Compute `abs(a - b) / max(a, b)` for sibling or repeated spans.

**Why it matters**
Latency spikes correlate strongly with downstream divergence in reasoning or tool behavior.

**Where it appears**

* Langfuse latency charts
* Arize performance dashboards

---

## 4.2 Timing Drift in Cyclic Steps

**Definition**
In loops or periodic actions, step durations widen or shrink unpredictably.

**How to detect**

* Compare consecutive iterations of similar span types.

**Why it matters**
Signals degraded model confidence, retry storms, or silent contention.

---

## 4.3 Interleaved Execution

**Definition**
Previously ordered spans begin overlapping in irregular ways.

**How to detect**

* Examine timestamp ordering of related spans.

**Why it matters**
May indicate concurrency races, tool pipeline backlog, or unstable reasoning.

---

# 5. Semantic Instability Patterns

## 5.1 Nested Tool Inconsistency

**Definition**
Multi-hop tool chains start with consistent arguments but gradually develop small mismatches.

**How to detect**

* Compare arguments or payload structure across hops.
* Look for field omissions, shape changes, or semantic shifts.

**Why it matters**
A top predictor of eventual workflow failure.

---

## 5.2 Self-Correction Oscillation

**Definition**
Model alternates between two or more incompatible reasoning paths.

**How to detect**

* Repeated A → B → A cycles in thought or tool signatures.

**Why it matters**
Strong sign that a correction loop is unstable or that the system lacks a clear convergence point.

---

## 5.3 Shrinkage of Arguments or Outputs

**Definition**
Arguments, tool params, or reasoning summaries become progressively smaller or less informative.

**How to detect**

* Compare argument size across steps.
* Detect decreasing field count.

**Why it matters**
Often indicates **loss of state**, **context erosion**, or **short-horizon reasoning collapse**.

---

# 6. Composite Patterns

These patterns combine multiple signals and often correspond to major failures.

## 6.1 Instability Cascade

Structural divergence → latency spikes → semantic mismatch → visible failure.

## 6.2 Silent Drift → Late Correction

The system shows structural and semantic instability long before explicit errors or retries appear.

## 6.3 Correction Loop Saturation

The agent repeatedly enters corrective behavior but never stabilizes.

---

# 7. How to Extend This Catalog

Additions should follow a simple rule:

> **If it can be derived from trace shape, arguments, metadata, or timing — it belongs here.**

New entries can be:

* framework-specific examples,
* new metrics tied to patterns,
* visual diagnostics,
* comparative studies using synthetic traces.

---

# 8. Summary

This catalog gives practitioners a shared vocabulary for describing instability patterns using only **observability-ready signals** like:

* trace structure,
* latency patterns,
* repeated spans,
* argument drift.

It helps unify intuition across Langfuse, Arize, LangChain, and LlamaIndex without any dependency on internal governance frameworks.

---

End of Document.
