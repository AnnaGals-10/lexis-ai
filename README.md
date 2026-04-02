# Lexis AI — Contract Analyzer

> Automatic risk detection, clause-level analysis and negotiation suggestions for any legal document.

Built with **LangChain**, **RAG (Retrieval-Augmented Generation)**, **OpenAI** and **Streamlit**.

---

## Features

- **Risk clause detection** — identifies abusive, ambiguous or unfavorable clauses with risk level (high / medium / low)
- **Industry benchmarks** — compares each clause against market standards with concrete numbers
- **Negotiation suggestions** — proposes fairer reformulations for each risky clause
- **Risk scoring** — overall contract risk score (1–10) with recommendation: Accept / Negotiate / Reject
- **Executive summary** — contract type, parties, duration, key points and main obligations
- **Contextual chat** — ask any question about the contract in natural language
- **PDF report export** — downloadable professional report with all findings
- **Analysis history** — keeps track of previously analyzed contracts
- **Multi-language** — automatically detects the contract language and responds accordingly

---

## Demo

![Lexis AI Demo](assets/demo.gif)

---

## How it works

```
PDF → chunks → embeddings → FAISS vector store → LLM (gpt-4o-mini) → structured analysis
```

1. The contract is split into overlapping chunks and embedded with OpenAI Embeddings
2. Chunks are stored in a FAISS vector store for semantic retrieval
3. Each analysis (red flags, score, summary, negotiations) queries the vector store with a specialized prompt
4. Results are structured as JSON and rendered in the Streamlit UI

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/lexis-ai.git
cd lexis-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your API key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

`.env.example`:
```
OPENAI_API_KEY=your-key-here
```

### 4. Create the contracts folder
```bash
mkdir contracts
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## Project structure

```
lexis-ai/
├── app.py                  # Streamlit UI
├── analyzer.py             # RAG pipeline & analysis logic
├── report_generator.py     # PDF report generation (ReportLab)
├── history.json            # Local analysis history
├── requirements.txt
├── .env.example
├── .gitignore
└── contracts/              # (gitignored) place your PDFs here
```

---

## Tech stack

| Component | Technology |
|-----------|------------|
| LLM | GPT-4o-mini (OpenAI) |
| Embeddings | OpenAI Embeddings |
| Vector store | FAISS (local) |
| RAG framework | LangChain |
| UI | Streamlit |
| PDF generation | ReportLab |
| PDF parsing | PyPDF |

---

## Author

Anna Galstyan Galoyan — Universitat Politècnica de Catalunya (UPC)
Grau en Intel·ligència Artificial, 2025–2026
