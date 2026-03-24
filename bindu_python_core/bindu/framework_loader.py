from typing import Dict, Optional

from .framework_registry import FrameworkRecord, FrameworkRegistry


class FrameworkLoader:
    def __init__(self, registry: Optional[FrameworkRegistry] = None):
        self.registry = registry or FrameworkRegistry()

    def load_text(self, record: FrameworkRecord) -> str:
        return record.absolute_path.read_text(encoding="utf-8")

    def load_by_id(self, framework_id: str) -> Optional[str]:
        record = self.registry.by_id(framework_id)
        if record is None:
            return None
        return self.load_text(record)

    def load_canonical_texts(self) -> Dict[str, str]:
        loaded: Dict[str, str] = {}
        for record in self.registry.canonical():
            if record.active:
                loaded[record.id] = self.load_text(record)
        return loaded

    def load_domain_texts(self, domain: str) -> Dict[str, str]:
        loaded: Dict[str, str] = {}
        for record in self.registry.by_domain(domain):
            if record.active:
                loaded[record.id] = self.load_text(record)
        return loaded