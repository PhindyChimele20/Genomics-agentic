from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from agents.state import AgentState
from agents.prompts import (
    PLANNER_PROMPT, INSPECTOR_PROMPT, PIPELINE_PROMPT, INTERPRETER_PROMPT
)
from tools.vcf_tools import summarize_vcf
from tools.report_tools import make_repro_pack_artifacts

def _extract_facts(file_manifest: List[Dict[str, Any]]) -> Dict[str, Any]:
    facts: Dict[str, Any] = {"files": file_manifest, "vcf_summaries": []}
    for f in file_manifest:
        name = f["name"].lower()
        path = f["path"]
        if name.endswith(".vcf") or name.endswith(".vcf.gz"):
            try:
                facts["vcf_summaries"].append(summarize_vcf(path))
            except Exception as e:
                facts["vcf_summaries"].append({"vcf_path": path, "error": str(e)})
    return facts

def _llm_call(llm: ChatOpenAI, system_prompt: str, payload: Dict[str, Any]) -> str:
    msg = f"""Payload (JSON-like):
{payload}
"""
    resp = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": msg},
    ])
    return resp.content

def node_facts(state: AgentState) -> AgentState:
    state["facts"] = _extract_facts(state.get("file_manifest", []))
    return state

def node_plan(state: AgentState) -> AgentState:
    llm = state["_llm"]
    payload = {"user_goal": state["user_goal"], "facts": state.get("facts", {})}
    state["plan_md"] = _llm_call(llm, PLANNER_PROMPT, payload)
    return state

def node_inspect(state: AgentState) -> AgentState:
    llm = state["_llm"]
    payload = {"user_goal": state["user_goal"], "facts": state.get("facts", {})}
    state["inspection_md"] = _llm_call(llm, INSPECTOR_PROMPT, payload)
    return state

def node_pipeline(state: AgentState) -> AgentState:
    llm = state["_llm"]
    payload = {
        "user_goal": state["user_goal"],
        "facts": state.get("facts", {}),
        "plan_md": state.get("plan_md", ""),
    }
    pipeline_md = _llm_call(llm, PIPELINE_PROMPT, payload)
    state["pipeline_md"] = pipeline_md

    artifacts = make_repro_pack_artifacts(
        user_goal=state["user_goal"],
        plan_md=state.get("plan_md", ""),
        inspection_md=state.get("inspection_md", ""),
        pipeline_md=pipeline_md,
    )
    state["artifacts"] = artifacts
    state["repro_pack_md"] = artifacts.get("README_repro.md", "")
    return state

def node_interpret(state: AgentState) -> AgentState:
    llm = state["_llm"]
    payload = {
        "user_goal": state["user_goal"],
        "facts": state.get("facts", {}),
        "plan_md": state.get("plan_md", ""),
        "pipeline_md": state.get("pipeline_md", ""),
    }
    state["interpretation_md"] = _llm_call(llm, INTERPRETER_PROMPT, payload)
    return state

def run_graph(user_goal: str, file_manifest: List[Dict[str, Any]], model: str, temperature: float) -> Dict[str, Any]:
    llm = ChatOpenAI(model=model, temperature=temperature)

    graph = StateGraph(AgentState)
    graph.add_node("facts", node_facts)
    graph.add_node("plan", node_plan)
    graph.add_node("inspect", node_inspect)
    graph.add_node("pipeline", node_pipeline)
    graph.add_node("interpret", node_interpret)

    graph.set_entry_point("facts")
    graph.add_edge("facts", "plan")
    graph.add_edge("plan", "inspect")
    graph.add_edge("inspect", "pipeline")
    graph.add_edge("pipeline", "interpret")
    graph.add_edge("interpret", END)

    app = graph.compile()

    init_state: AgentState = {
        "user_goal": user_goal,
        "file_manifest": file_manifest,
        "_llm": llm,  # internal
        "artifacts": {},
    }

    out = app.invoke(init_state)
    # Remove non-serializable items
    out.pop("_llm", None)
    return out
