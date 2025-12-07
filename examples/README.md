# Examples

This directory contains **concrete, scenario-driven demonstrations** of early instability patterns in multi-turn agents.

It serves two purposes:

* Provide **intuitive, narrative examples** that illustrate how instability appears in real traces.
* Offer **small reproducible experiments** (Markdown, Python, and notebooks) that let you explore metrics and patterns hands-on.

---

## 📁 What’s inside

### 1. Narrative scenario examples (Markdown)

These files describe specific instability phenomena in small, easy‑to‑understand agent setups:

* **`long-horizon-toy-agent.md`**

  * A miniature agent designed to run 20–40 steps and exhibit long-horizon wobble.
  * Useful for studying latency drift, micro‑repairs, and early misalignment patterns.

* **`tool-chain-instability.md`**

  * Demonstrates how tool-call chains drift when signatures diverge or arguments slowly shift.
  * Focuses on nested tool-call inconsistency and unstable tool semantics.

* **`workflow-looping.md`**

  * An example of runaway loops, repeated reasoning cycles, and state overrun.
  * Shows early signals that predict looping before the loop visibly begins.

These files emphasize clear storytelling, diagrams, and structural signals.

---

## 🧪 Notebooks (`notebooks/`)

Interactive experiments for working with traces:

* **`01_inspect_trace_tree.ipynb`**

  * Inspect hierarchical trace structures.
  * Visualize sibling divergences and partial matches.

* **`02_early_instability_metrics.ipynb`**

  * Compute and visualize metrics such as relative latency gaps and recovery-turn-distance.
  * Compare multiple sessions side-by-side.

* **`03_visualize_trace_divergence.ipynb`**

  * Draw structural divergence diagrams.
  * Explore pattern detection thresholds.

The notebooks use only lightweight dependencies (`pandas`, `numpy`, `matplotlib`).

---

## 🧬 Synthetic traces (`synthetic_traces/`)

These are small JSONL files designed to test ideas quickly:

* **`simple_correction_loop.jsonl`**

  * A compact scenario showing: drift → correction → recovery → continue.

* **`noisy_mixed_sessions.jsonl`**

  * A more realistic dataset with:

    * noisy latencies
    * partial tool failures
    * variable depth
    * mixed outcomes

* **`generate_synthetic_traces.py`**

  * A tiny generator script that creates new synthetic sessions with controllable levels of noise and instability.

---

## 🛠 Utility scripts (`scripts/`)

These scripts rely on the examples directory and are often used together:

* **`compute_metrics_from_jsonl.py`**

  * Compute instability-focused metrics directly from trace files.

* **`trace_tree_sanity_checks.py`**

  * Basic checks for timestamp monotonicity, ID consistency, and structural anomalies.

---

## 🎯 How to start exploring

1. Open a notebook under `examples/notebooks/`.
2. Load one of the synthetic JSONL traces.
3. Run visualizations such as:

   * trace-tree structure
   * divergence sketches
   * latency-gap plots
4. Compare against your own logs.

This directory is intentionally lightweight and is meant to serve as a **playground** for understanding how multi-turn agents become unstable — long before user-visible failures occur.

---

If you’d like additional scenario files or you want to contribute new examples, feel free to propose them in an issue or pull request.
