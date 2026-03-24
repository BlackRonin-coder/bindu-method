from dataclasses import dataclass, field
from typing import Dict, List

from .framework_loader import FrameworkLoader
from .framework_registry import FrameworkRecord, FrameworkRegistry


@dataclass
class CandidateAction:
    name: str
    description: str
    expected_outcome: str
    fallback_plan: str
    measurable_outputs: List[str] = field(default_factory=list)
    frameworks_used: List[str] = field(default_factory=list)


@dataclass
class KernelResponse:
    subject: str
    request: str
    domain: str
    selected_frameworks: List[str] = field(default_factory=list)
    candidate_actions: List[CandidateAction] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "subject": self.subject,
            "request": self.request,
            "domain": self.domain,
            "selected_frameworks": self.selected_frameworks,
            "candidate_actions": [
                {
                    "name": action.name,
                    "description": action.description,
                    "expected_outcome": action.expected_outcome,
                    "fallback_plan": action.fallback_plan,
                    "measurable_outputs": action.measurable_outputs,
                    "frameworks_used": action.frameworks_used,
                }
                for action in self.candidate_actions
            ],
        }


class BinduKernel:
    def __init__(self, registry: FrameworkRegistry | None = None, loader: FrameworkLoader | None = None):
        self.registry = registry or FrameworkRegistry()
        self.loader = loader or FrameworkLoader(self.registry)

    def detect_domain(self, subject: str, request: str) -> str:
        text = f"{subject} {request}".lower()

        if "housing" in text or "home" in text or "delivery" in text:
            return "home"

        return "generic"

    def select_frameworks(self, domain: str) -> List[FrameworkRecord]:
        selected: List[FrameworkRecord] = []

        for record in self.registry.active():
            if record.layer in {"ethical_governor", "kernel", "logic_proofing", "governance"}:
                selected.append(record)

        if domain != "generic":
            for record in self.registry.by_domain(domain):
                if record.active and record not in selected:
                    selected.append(record)

        return selected

    def build_actions(self, domain: str, frameworks: List[FrameworkRecord]) -> List[CandidateAction]:
        framework_ids = [record.id for record in frameworks]

        if domain == "home":
            return [
                CandidateAction(
                    name="home_multi_channel_supply_fix",
                    description="Reduce planning friction, widen delivery channels, and keep the housing system tied to real delivery rather than paper movement.",
                    expected_outcome="Improved housing delivery under planning and capital constraints.",
                    fallback_plan="Reduce to one local delivery zone, verify throughput, then scale.",
                    measurable_outputs=[
                        "approvals_to_completion_time",
                        "housing_supply_gain",
                        "lived_outcome_signal",
                    ],
                    frameworks_used=framework_ids,
                ),
                CandidateAction(
                    name="home_sme_modular_pathway",
                    description="Support SME and modular delivery routes so the system is not dependent on one narrow supply channel.",
                    expected_outcome="More resilient and faster housing delivery pathways.",
                    fallback_plan="Pilot through one verified local pathway before broad rollout.",
                    measurable_outputs=[
                        "sme_builder_participation",
                        "modular_delivery_rate",
                        "delivery_time_reduction",
                    ],
                    frameworks_used=framework_ids,
                ),
            ]

        return [
            CandidateAction(
                name="generic_structural_diagnosis",
                description="Run a structural diagnosis first, identify the real blockage, then choose the smallest viable correction.",
                expected_outcome="A clearer understanding of the real system constraint before intervention.",
                fallback_plan="Reduce scope to one subsystem and re-run bounded diagnosis.",
                measurable_outputs=[
                    "constraint_identification_quality",
                    "intervention_clarity",
                ],
                frameworks_used=framework_ids,
            )
        ]

    def run_wl(self, subject: str, request: str) -> KernelResponse:
        domain = self.detect_domain(subject, request)
        frameworks = self.select_frameworks(domain)

        for record in frameworks:
            if record.absolute_path.exists():
                self.loader.load_text(record)

        actions = self.build_actions(domain, frameworks)

        return KernelResponse(
            subject=subject,
            request=request,
            domain=domain,
            selected_frameworks=[record.id for record in frameworks],
            candidate_actions=actions,
        )