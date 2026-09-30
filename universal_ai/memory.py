import json
from pathlib import Path

from universal_ai.config import MEMORY_PATH


class MemoryStore:
    def __init__(self, path: Path | None = None):
        self.path = path or MEMORY_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def load(self):
        try:
            content = self.path.read_text(encoding="utf-8")
            data = json.loads(content)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save(self, records):
        self.path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    def append(self, role, content):
        records = self.load()
        records.append({"role": role, "content": content})
        self.save(records)

    def recent(self, limit=10):
        records = self.load()
        return records[-limit:]
