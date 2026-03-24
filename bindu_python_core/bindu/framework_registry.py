from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import json


@dataclass
class FrameworkRecord:
    id: str
    title: str
    layer: str
    status: str
    authority_rank: int
    version: str
    active: bool
    file_path: str
    domain: Optional[str] = None

    @property
    def absolute_path(self) -> Path:
        base_dir = Path(__file__).resolve().parent.parent
        return base_dir / self.file_path


class FrameworkRegistry:
    def __init__(self, manifest_path: Optional[Path] = None):
        base_dir = Path(__file__).resolve().parent.parent
        self.manifest_path = Path(manifest_path) if manifest_path else base_dir / "framework_manifest.json"
        self._records: List[FrameworkRecord] = []
        self.reload()

    def reload(self) -> None:
        raw = self.manifest_path.read_text(encoding="utf-8")
        data = json.loads(raw)

        self._records = [
            FrameworkRecord(
                id=item["id"],
                title=item["title"],
                layer=item["layer"],
                status=item["status"],
                authority_rank=item["authority_rank"],
                version=item["version"],
                active=item["active"],
                file_path=item["file_path"],
                domain=item.get("domain")
            )
            for item in data.get("frameworks", [])
        ]

        self._records.sort(key=lambda record: record.authority_rank)

    def all(self) -> List[FrameworkRecord]:
        return list(self._records)

    def active(self) -> List[FrameworkRecord]:
        return [record for record in self._records if record.active]

    def canonical(self) -> List[FrameworkRecord]:
        return [record for record in self._records if record.status == "canonical"]

    def by_id(self, framework_id: str) -> Optional[FrameworkRecord]:
        for record in self._records:
            if record.id == framework_id:
                return record
        return None

    def by_domain(self, domain: str) -> List[FrameworkRecord]:
        return [record for record in self._records if record.domain == domain]

    def highest_authority(self) -> Optional[FrameworkRecord]:
        if not self._records:
            return None
        return self._records[0]