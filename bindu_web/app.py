

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_FILE = BASE_DIR / "frontend.html"


class BinduRequest(BaseModel):
    subject: str
    request: str
    purpose: str = ""
    constraints: list = []
    legal_constraints: list = []
    assumptions: list = []
    metadata: dict = {}


@app.get("/", response_class=HTMLResponse)
def home():
    return FRONTEND_FILE.read_text(encoding="utf-8")


@app.post("/run-bindu")
def run_bindu(payload: BinduRequest):
    subject = payload.subject
    request = payload.request
    command = payload.metadata.get("command", "")

    candidate_actions = [
        {
            "name": "home_multi_channel_supply_fix",
            "description": "Reduce planning friction, simplify housing delivery pathways, preserve dignity, acknowledge lived reality, increase multi-channel supply, reduce friction, and iterate continuously with legally compliant delivery.",
            "expected_outcome": "Improved housing delivery outcome under planning and capital constraints.",
            "measurable_outputs": [
                "approvals_to_completion_time",
                "housing_supply_gain",
                "lived_outcome_signal"
            ],
            "fallback_plan": "Reduce to local delivery zone, prove throughput, then scale.",
            "patches_applied": [
                "HOME_adapter",
                command
            ]
        },
        {
            "name": "home_sme_modular_pathway",
            "description": "Simplify approvals for SME builders, reduce friction for modular and offsite delivery, preserve dignity, acknowledge lived reality, and keep the system anchored to outcome.",
            "expected_outcome": "Broader housing delivery base with improved resilience and delivery speed.",
            "measurable_outputs": [
                "sme_builder_participation",
                "modular_delivery_rate",
                "delivery_time_reduction"
            ],
            "fallback_plan": "Pilot in one borough or local zone before broader rollout.",
            "patches_applied": [
                "HOME_adapter",
                command
            ]
        }
    ]

    return {
        "subject": subject,
        "request": request,
        "command": command,
        "candidate_actions": candidate_actions
    }
