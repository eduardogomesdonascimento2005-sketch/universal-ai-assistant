import json
import re
import subprocess
import urllib.parse
from pathlib import Path

import requests

from config import PROJECT_ROOT


class ToolRegistry:
    def __init__(self):
        self.root = PROJECT_ROOT

    def list_dir(self, path: str = "."):
        target = self._resolve(path)
        return [
            {"name": item.name, "type": "dir" if item.is_dir() else "file", "path": str(item)}
            for item in sorted(target.iterdir())
        ]

    def read_file(self, path: str):
        target = self._resolve(path)
        return target.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str):
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"status": "ok", "path": str(target)}

    def run_command(self, command: str):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=str(self.root))
            output = (result.stdout or "") + (result.stderr or "")
            return {"returncode": result.returncode, "output": output.strip()[:4000]}
        except Exception as exc:
            return {"returncode": 1, "output": str(exc)}

    def search_web(self, query: str):
        try:
            url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode({
                "q": query,
                "format": "json",
                "no_redirect": 1,
                "no_html": 1,
            })
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            payload = response.json()
            results = []
            if payload.get("AbstractText"):
                results.append({"title": payload.get("Heading") or "Resumo", "snippet": payload.get("AbstractText")})
            for item in payload.get("RelatedTopics", [])[:5]:
                if isinstance(item, dict) and "Text" in item:
                    results.append({"title": item.get("Name") or "Relacionado", "snippet": item.get("Text")})
            return {"query": query, "results": results[:5]}
        except Exception as exc:
            return {"query": query, "error": str(exc), "results": []}

    def _resolve(self, path: str):
        if path in {".", "", None}:
            return self.root
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = (self.root / candidate).resolve()
        return candidate


def parse_tool_request(user_message: str):
    text = user_message.strip().lower()

    if any(word in text for word in ["listar", "lista", "arquivos", "mostre os arquivos"]) :
        return {"tool": "list_dir", "args": {"path": "."}}

    if "leia" in text or "ler" in text or "arquivo" in text:
        match = re.search(r"(?:arquivo|ler|leia|leitura)\s+[\'\"]?([^\'\"\n]+)[\'\"]?", user_message, re.IGNORECASE)
        if match:
            return {"tool": "read_file", "args": {"path": match.group(1).strip()}}

    if "escreva" in text or "crie" in text or "salve" in text or "grava" in text:
        path_match = re.search(r"(?:em|no|na|arquivo)\s+[\'\"]?([^\'\"\n]+)[\'\"]?", user_message, re.IGNORECASE)
        if path_match:
            return {
                "tool": "write_file",
                "args": {
                    "path": path_match.group(1).strip(),
                    "content": "Conteúdo gerado pela IA profissional."
                },
            }

    if any(word in text for word in ["execute", "rode", "executa", "comando", "terminal"]):
        match = re.search(r"(?:execute|rode|executa|comando|terminal)\s+(.*)", user_message, re.IGNORECASE)
        if match:
            return {"tool": "run_command", "args": {"command": match.group(1).strip()}}

    if any(word in text for word in ["pesquise", "procure", "buscar", "search"]):
        match = re.search(r"(?:pesquise|procure|buscar|search)\s+(.*)", user_message, re.IGNORECASE)
        if match:
            return {"tool": "search_web", "args": {"query": match.group(1).strip()}}

    return None
