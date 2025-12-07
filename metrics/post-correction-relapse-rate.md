# Post‑Correction Relapse Rate

> A simple, trace‑based metric for quantifying how often a session appears to recover — then drifts again.

---

## 🧩 What this metric captures

In multi‑turn agents, a flow often **looks stable again** after a correction: tool arguments match constraints, responses resume the expected pattern, latencies return to normal.

But sometimes the stability is temporary — the session drifts again.

**Post‑correction relapse rate** measures how often this happens.

This is one of the most reliable indicators that an agent has:

* shallow or inconsistent recovery behavior,
* unstable internal reasoning loops,
* or state that was “patched” but not fully realigned.

---

## 📐 Plain‑language definition

> Of all sessions that show *at least one correction*, what fraction experience **another drift event** later in the same session?

This can be computed using only JSONL traces with minimal structure (trace_id, timestamps, event types).

---

## 📊 When to use this metric

Use this when you want to understand:

* whether your correction mechanisms are *actually stabilizing* behavior,
* whether user or agent corrections "stick,"
* whether loops, retries, or misalignment tend to recur,
* whether longer sessions correlate with higher recurrence.

It is especially helpful for comparing:

* different prompting strategies,
* different runtime policies,
* different agent architectures or tools.

---

## 📁 Required trace structure

Minimal assumptions:

* each event has a **trace_id**,
* events appear in chronological order per trace,
* events include a **drift‑like signal** and a **correction‑like signal**.

Examples of signals you could treat as drift:

* constraint violation,
* tool‑call mismatch,
* missing required fields,
* user intent mismatch.

Examples of signals you could treat as correction:

* a retry with adjusted arguments,
* a clarifying question,
* a restated plan,
* an explicit repair pattern.

These definitions are intentionally flexible — the repo does not impose strict taxonomy.

---

## 🔢 Computation (from JSONL)

Pseudo‑algorithm for trace‑level computation:

```python
# For each session (grouped by trace_id):
had_correction = False
relapsed = False

for event in events:
    if is_correction(event):
        had_correction = True
    elif had_correction and is_drift(event):
        relapsed = True
        break  # further drift not needed

return had_correction, relapsed
```

Dataset‑level rate:

```python
relapse_rate = (number_of_sessions_with_relapse) / (number_of_sessions_with_correction)
```

---

## 🧠 Interpretation

A **high relapse rate** suggests:

* corrections are shallow,
* internal state is not truly recovered,
* multi‑turn reasoning continues drifting later,
* tools or retrieval introduce inconsistent signals,
* user re‑direction is not strong enough.

A **low relapse rate** suggests:

* corrections reliably stabilize behavior,
* recovery patterns are strong,
* the agent’s internal loop is resilient.

---

## 🕳️ Pitfalls & edge cases

* Sessions with **multiple corrections** may need stricter logic (e.g., count only first).
* Very short sessions inflate the “no relapse” denominator.
* A correction followed by session end does **not** count as relapse.
* Long‑horizon tasks tend to show higher relapse simply due to larger surface area.
* Tool‑driven flows may show “silent relapse” in planning spans (detectable via latency or divergence).

---

## 📈 Optional extensions

Advanced variants you can compute:

### 1. **Relapse Turn Distance**

How many turns after correction does relapse occur?

### 2. **Severity‑Weighted Relapse**

Weight later drift by strength/impact.

### 3. **Relapse Clusters**

Group sessions by where relapse tends to occur (early, mid, late).

These extensions integrate naturally with other metrics in this repo (e.g., recovery‑turn‑distance, trace‑tree‑divergence).

---

## ✅ Summary

**Post‑Correction Relapse Rate** is one of the simplest but most revealing metrics for understanding whether your correction mechanisms are truly stabilizing multi‑turn agents.

It answers the practical question:

> "When we fix a session, does it actually stay fixed?"

---

If you'd like, I can also generate:

* plotting utilities,
* notebook examples,
* CLI integration for `compute_metrics_from_jsonl.py`.
