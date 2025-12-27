# 🧠 The Clinical Feedback Loop: Semantic Memory

The most critical innovation in Clinical Copilot is its ability to learn from the clinicians who use it. This document details the **Validation Terminal** and how it power's the system's "long-term memory."

---

## 🛠️ The Validation Terminal (UI)

Located at the bottom of the Assessment panel, the Validation Terminal gives doctors the final word.

### 1. Approve vs. Correct
- **Approve (Green)**: Signals that the ML risk and LLM differential are accurate. This reinforces the current pattern in the RAG engine.
- **Correct (Red)**: Signals an outlier or error. Doctors are encouraged to provide specific notes on *why* the AI was incorrect (e.g., "Patient has rare genetic condition X not captured by sensors").

### 2. "Commit to Memory"
When a clinician clicks "Commit to Memory," the feedback is synchronized across the distributed cluster.
- **WebSocket Update**: The dashboard displays a "Memory Synchronized" pulse.
- **RAG Update**: The feedback (Patient Vitals + Doctor Notes) is indexed in the PostgreSQL database for future semantic retrieval.

---

## 🔄 How the System Learns (RAG-Lite Flow)

Whenever a **new** patient is assessed, the backend performs a **Semantic Vector Search**:

1. **Calculate Distance**: It finds patients from the "Memory" with similar Age, BP, Glucose, and BMI using **Normalized Euclidean Distance**.
2. **Context Injection**:
   - If a previous doctor said "This pattern likely indicates early Stage 2 Hypertension," that note is injected into the Gemini/GPT-4o prompt.
   - The AI is instructed: *"A clinician previously noted [Note] for a very similar case. Incorporate this expertise into your current assessment."*

---

## 📈 Human-in-the-Loop Value

This feedback loop solves the "AI Hallucination" problem in three ways:
1. **Clinical Correction**: If the AI misses a nuance, the human correction becomes a permanent part of the context for future similar patients.
2. **Knowledge Transfer**: Notes from a senior cardiologist can automatically "assist" a junior resident if their patients share similar biometric profiles.
3. **Data Quality**: The system builds a proprietary, high-quality "Labeled Clinical Experience" dataset over time.

---
*"The AI proposes, the clinician disposes, the system remembers."*
