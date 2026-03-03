import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

from agents.graph import run_graph
from tools.file_sniffer import save_uploads_to_tempdir

load_dotenv()

st.set_page_config(page_title="Genomics Agentic Research Copilot", layout="wide")
st.title("Genomics Agentic Research Copilot")
st.caption("Multi-agent assistant for MSc/PhD genomics workflows: planning, QC, pipeline scripts, interpretation.")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    st.divider()
    st.write("Upload genomics files (optional)")
    uploads = st.file_uploader(
        "VCF/TSV/BAM/QC outputs",
        accept_multiple_files=True,
        type=["vcf", "gz", "tsv", "csv", "txt", "bam", "bai", "eigenvec", "eigenval", "q", "fam", "bim", "bed"]
    )

st.subheader("Your research question / goal")
user_goal = st.text_area(
    "Example: 'Assess population structure and detect admixture between Namibia vs South Africa in Argyrosomus inodorus.'",
    height=120
)

run_btn = st.button("Run agents", type="primary", disabled=(not user_goal.strip()))

if run_btn:
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY not found. Add it to a .env file or your environment variables.")
        st.stop()

    with st.spinner("Running multi-agent workflow..."):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_manifest = save_uploads_to_tempdir(uploads, tmpdir) if uploads else []
            result = run_graph(
                user_goal=user_goal.strip(),
                file_manifest=file_manifest,
                model=model,
                temperature=temperature,
            )

    # Layout results
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Plan")
        st.markdown(result.get("plan_md", ""))
        st.subheader("Data inspection")
        st.markdown(result.get("inspection_md", ""))

    with col2:
        st.subheader("Pipeline scripts")
        st.markdown(result.get("pipeline_md", ""))
        st.subheader("Interpretation & caveats")
        st.markdown(result.get("interpretation_md", ""))

    st.subheader("Reproducibility pack")
    st.markdown(result.get("repro_pack_md", ""))

    # Downloadable artifacts
    st.subheader("Downloads")
    for name, content in result.get("artifacts", {}).items():
        st.download_button(
            label=f"Download {name}",
            data=content.encode("utf-8"),
            file_name=name,
            mime="text/plain"
        )
