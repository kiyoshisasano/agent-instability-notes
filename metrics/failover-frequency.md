# Failover Frequency (FF)

> **What fraction of sessions fall back to an alternate execution path?**
> A measure of how often an agent abandons its primary workflow due to instability, policy violation, or unrecoverable errors.

---

## 1. Motivation

Many multi-turn agents include a backup or alternate path:

* a safer but slower strategy,
* a fallback retrieval method,
* a reduced-capability reasoning mode,
* or a policy-driven shutdown.

Frequent failover is often a **late-stage instability indicator**. It usually means:

* repairs are not stabilizing behavior,
* drift is recurring,
* or the system is hitting safety/validation boundaries.

Failover Frequency (FF) captures how often this happens.

---

## 2. Definition (Plain Language)

**Failover Frequency** is the proportion of lifecycle events that represent a failover transition.

It answers the question:

> "Out of all meaningful agent lifecycle events, how many indicate the system had to fall back?"

This is intentionally simple: it gives a coarse but reliable sense of whether fallback pathways are common or rare.

---

## 3. How to Compute

### 3.1 Required Fields

From each JSONL event, you need:

* `event_type`
* `pld.phase` or `phase`

### 3.2 Event Filtering Rules

Count only **lifecycle events**, excluding:

* `phase = none`
* debug / infrastructure-only items
* purely informational logs

Typical lifecycle phases:

```
drift
repair
reentry
continue
outcome
failover
```

### 3.3 Formula

```
FF = (# of failover events) / (# of lifecycle events)
```

Both counts come from the **same session or dataset**, depending on context.

### 3.4 Example

```
Total lifecycle events: 120
Failover events: 6
FF = 6 / 120 = 0.05 → 5%
```

---

## 4. Interpretation

### **Low FF (<1%)**

Generally healthy. Failover is rare.

### **Moderate FF (1–5%)**

Some workflows may be fragile under load or noisy contexts.

### **High FF (>5%)**

Clear sign that fallback is happening too often. Likely causes:

* recurring drift episodes,
* unstable tool usage,
* brittle recovery logic,
* overly strict validation rules.

High FF typically pairs with:

* long recovery latency,
* high relapse rates,
* noisy divergence patterns.

---

## 5. Caveats

* Fallback behavior must be **defined**; otherwise FF is meaningless.
* A high FF is not always bad—sometimes failover is the correct policy under risk.
* Compare across sessions, models, or deployments—not across unrelated systems.
* FF reflects **frequency**, not **severity**.

---

## 6. Quick Computation Snippet

```python
from collections import Counter
import jsonlines

def failover_frequency(path):
    lifecycle = 0
    failover = 0

    with jsonlines.open(path) as reader:
        for e in reader:
            phase = e.get("phase") or e.get("pld", {}).get("phase")
            if phase in (None, "none"):
                continue

            lifecycle += 1
            if phase == "failover":
                failover += 1

    return failover / lifecycle if lifecycle > 0 else 0.0
```

---

## 7. When to Use

Use Failover Frequency when you want a simple, robust indicator that your agent:

* prematurely abandons tasks,
* collapses into fallback modes,
* or repeatedly fails to stay on the primary path.

FF is one of the most **interpretable** instability metrics and a good first signal when evaluating new models or orchestration designs.

---
