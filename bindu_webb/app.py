from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

RUNTIME_ROOT = Path(__file__).resolve().parent.parent
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from bindu_runtime import WLEngine, BinduContext  # type: ignore

app = FastAPI(title="Bindu Web API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = WLEngine(str(Path(__file__).resolve().parent / "bindu_web_runtime.db"))


class SolveRequest(BaseModel):
    subject: str = Field(default="housing_delivery_system")
    request: str
    purpose: str = ""
    constraints: List[str] = Field(default_factory=list)
    legal_constraints: List[str] = Field(default_factory=list)
    human_impact: Optional[str] = None
    assumptions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


@app.get("/", response_class=HTMLResponse)
def serve_frontend() -> str:
    html_path = Path(__file__).parent / "frontend.html"
    return html_path.read_text(encoding="utf-8")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/solve")
def solve(req: SolveRequest) -> Dict[str, Any]:
    command = req.metadata.get("command", "WL")
    request_text = req.request.strip()
    if request_text and not request_text.upper().startswith(command.upper()):
        request_text = f"{command} {request_text}"

    ctx = BinduContext(
        subject=req.subject,
        request=request_text,
        purpose=req.purpose,
        constraints=req.constraints,
        legal_constraints=req.legal_constraints,
        human_impact=req.human_impact,
        assumptions=req.assumptions,
        metadata=req.metadata,
    )

    hidden = engine.kernel.reasoning_layer.detect(ctx)
    candidate_actions = engine.kernel.generator.generate(ctx)

    task_id = engine.submit_context(ctx)
    result = engine.run_once()

    if result is None:
        return {"error": "No task processed"}

    canonical = engine.kernel.store.get_canonical("alignment_snapshot") or {}

    return {
        "task_id": task_id,
        "structural_read": {
            "subject": ctx.subject,
            "request": ctx.request,
            "purpose": ctx.purpose,
            "constraints": ctx.constraints,
            "hidden_reasoning": hidden,
        },
        "candidate_actions": [
            {
                "name": action.name,
                "description": action.description,
                "expected_outcome": action.expected_outcome,
                "measurable_outputs": action.measurable_outputs,
                "fallback_plan": action.fallback_plan,
                "patches_applied": action.patches_applied,
            }
            for action in candidate_actions
        ],
        "result": {
            "status": result.status.value,
            "alignment_score": result.alignment_score,
            "survivability_score": result.survivability_score,
            "wisdom_score": result.wisdom_score,
            "outcome_score": result.outcome_score,
            "utility_score": result.utility_score,
            "drift_severity": result.drift_severity.value,
            "reasons": result.reasons,
            "selected_action": {
                "name": result.selected_action.name if result.selected_action else None,
                "description": result.selected_action.description if result.selected_action else None,
                "expected_outcome": result.selected_action.expected_outcome if result.selected_action else None,
                "fallback_plan": result.selected_action.fallback_plan if result.selected_action else None,
                "measurable_outputs": result.selected_action.measurable_outputs if result.selected_action else [],
                "patches_applied": result.selected_action.patches_applied if result.selected_action else [],
                "legal_notes": result.selected_action.legal_notes if result.selected_action else [],
            },
        },
        "canonical_state": canonical,
    }
