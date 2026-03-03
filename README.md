#  Genomics Agentic Research   AI (Streamlit)

Agentic AI assistant for MSc/PhD genomics workflows: planning, file inspection, pipeline generation, and interpretation.

## Features
- Multi-agent orchestration (Planner / Inspector / Pipeline Builder / Interpreter)
- Upload genomics files (VCF, QC tables, PLINK outputs)
- Produces:
  - Analysis plan
  - Bash + HPC PBS templates
  - Interpretation + caveats
  - Reproducibility pack downloads

## Tech stack
- Streamlit
- LangGraph + LangChain
- OpenAI API
- Lightweight genomics file inspection (VCF header + quick scan)

## Run locally
```bash
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
