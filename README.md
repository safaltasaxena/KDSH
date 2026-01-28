# Narrative Consistency via Constraint Reasoning

This repository contains our submission for the **Kharagpur Data Science Hackathon (KDSH 2026)**.
The project tackles the problem of **global narrative consistency**: determining whether a *hypothetical backstory* of a character is logically and causally consistent with the *entire long-form narrative* (100k+ words) of a novel.

Unlike surface-level LLM reasoning, our approach explicitly **extracts, tracks, embeds, and evaluates long-term narrative constraints** and reduces the task to a principled **constraint consistency decision problem**.

---

## 🚀 Motivation

Large Language Models excel at local plausibility but often fail at **global consistency** across long narratives. They:

* Miss long-range contradictions
* Confuse similarity with causality
* Fail to accumulate evidence over time

This system replaces plausibility-based reasoning with **constraint-based reasoning**, ensuring that any proposed backstory respects the irreversible events, stable beliefs, traits, capabilities, and relationships established throughout the story.

---

## 🧠 Core Idea

Given:

1. A complete novel (no truncation)
2. A newly written, plausible hypothetical backstory

We ask:

> *Could this backstory logically and causally produce the observed narrative?*

The system outputs a **binary decision**:

* `1` → Backstory is globally consistent
* `0` → Backstory is globally inconsistent

---

## 🧩 Constraint Taxonomy

We model five types of long-term, non-reversible constraints:

1. **Belief Constraints**
   Stable worldviews inferred from repeated actions (e.g., distrusts authority).

2. **Trait Constraints**
   Persistent personality characteristics (e.g., loyal, impulsive).

3. **Capability Constraints**
   Skills or abilities that enable or prevent actions (e.g., can fight, cannot read).

4. **Irreversible Event Constraints**
   Permanent events that cannot be undone (e.g., death, betrayal).

5. **Relationship Constraints**
   Stable interpersonal relationships (e.g., loyal to X, hostile to Y).

### Constraint Severity

* **Hard Constraints** → Immediate failure (score = 0)
* **Soft Constraints** → Aggregated and thresholded

---

## 🏗️ System Architecture

```
Books (.txt)
   ↓
Chunking & Cleaning
   ↓
Constraint Extraction (LLM)
   ↓
Constraint Embedding (Vector Store)
   ↓
Backstory Claim Extraction
   ↓
Claim–Constraint Retrieval (Cosine Similarity)
   ↓
Contradiction Scoring
   ↓
Score Aggregation
   ↓
Binary Decision (0 / 1)
```

---

## 📁 Repository Structure

```
narrative-consistency/
│
├── docs/
│   ├── constraints.md            # Constraint taxonomy & theory
│   ├── problem_reformulation.md  # Formal task definition
│   └── why_llms_fail.md          # Motivation & failure modes
│
├── scripts/
│   ├── ingest_books.py           # Book ingestion & chunking
│   ├── extract_constraints.py    # Constraint extraction pipeline
│   ├── embed_constraints.py      # Embedding constraints using OpenAI
│   ├── extract_claims.py         # Backstory claim extraction
│   ├── check_stats.py            # Dataset statistics
│   └── diagnose_flatness.py      # Score distribution diagnostics
│
├── src/
│   ├── constraint_extractor.py   # Core constraint extraction logic
│   ├── claim_extractor.py        # Claim extraction logic
│   ├── contradiction_logic.py    # Soft/Hard contradiction scoring
│   └── decision.py               # Score aggregation & labeling
│
├── main.py                       # End-to-end consistency check
├── main_eval.py                  # Training evaluation & threshold tuning
├── main_day3.py                  # Pathway-based pipeline
├── requirements.txt
└── Problem_Statement.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/<your-username>/narrative-consistency.git
cd narrative-consistency
pip install -r requirements.txt
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your_api_key"
```

---

## ▶️ Running the Pipeline

### 1️⃣ Ingest and Chunk Books

```bash
python scripts/ingest_books.py
```

### 2️⃣ Extract Narrative Constraints

```bash
python scripts/extract_constraints.py
```

### 3️⃣ Embed Constraints

```bash
python scripts/embed_constraints.py
```

### 4️⃣ Extract Backstory Claims

```bash
python scripts/extract_claims.py
```

### 5️⃣ Evaluate Consistency

```bash
python main_eval.py
```

Or run a single backstory check:

```bash
python main.py
```

---

## 📊 Evaluation

* Retrieval via cosine similarity over embedded constraints
* Contradiction scoring via symbolic + LLM-assisted logic
* Aggregation via weighted accumulation
* Final decision via tunable threshold

Baseline comparison against majority label included.

---

## 🧪 Track Alignment

* **Track A (Systems Reasoning with NLP & GenAI)** ✅
* Uses Pathway for ingestion & orchestration
* Hybrid symbolic + neural reasoning
* Explicit long-context constraint tracking

---

## 🚫 Explicit Exclusions

To ensure robustness and interpretability, we do **not** model:

* Emotional states
* Literary symbolism
* Unreliable narration
* One-off actions
* Psychological speculation

---

## 🏁 Key Takeaway

> Narrative consistency is not about plausibility — it is about **respecting constraints over time**.

This system demonstrates how long-form reasoning can be reduced to a structured, testable decision problem.

---

## 👥 Team & Hackathon

**Kharagpur Data Science Hackathon 2026**
Organized in collaboration with **Pathway**

---

## 📄 License

MIT License
