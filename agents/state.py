from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict, total=False):
    user_goal: str
    file_manifest: List[Dict[str, Any]]  # [{"name":..., "path":..., "size":...}]
    facts: Dict[str, Any]

    plan_md: str
    inspection_md: str
    pipeline_md: str
    interpretation_md: str
    repro_pack_md: str

    artifacts: Dict[str, str]  # filename -> text content
