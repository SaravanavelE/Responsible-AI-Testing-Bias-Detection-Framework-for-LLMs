"""Multi-provider LLM client with JSON path extraction."""
import json
from typing import Any, Optional

import httpx
from jsonpath_ng import parse as jsonpath_parse

from app.core.encryption import vault


PROVIDER_PRESETS = {
    "openai": {
        "api_base_url": "https://api.openai.com/v1",
        "response_json_path": "choices[0].message.content",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "groq": {
        "api_base_url": "https://api.groq.com/openai/v1",
        "response_json_path": "choices[0].message.content",
        "models": ["grok-3-mini", "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
    },
    "gemini": {
        "api_base_url": "https://generativelanguage.googleapis.com/v1beta",
        "response_json_path": "candidates[0].content.parts[0].text",
        "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
    },
    "claude": {
        "api_base_url": "https://api.anthropic.com/v1",
        "response_json_path": "content[0].text",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
    },
    "ollama": {
        "api_base_url": "http://localhost:11434",
        "response_json_path": "message.content",
        "models": ["llama3", "mistral", "codellama"],
    },
    "deepseek": {
        "api_base_url": "https://api.deepseek.com/v1",
        "response_json_path": "choices[0].message.content",
        "models": ["deepseek-chat", "deepseek-coder"],
    },
    "azure_openai": {
        "api_base_url": "https://{resource}.openai.azure.com/openai/deployments/{deployment}",
        "response_json_path": "choices[0].message.content",
        "models": ["gpt-4o"],
    },
    "openrouter": {
        "api_base_url": "https://openrouter.ai/api/v1",
        "response_json_path": "choices[0].message.content",
        "models": ["openai/gpt-4o", "anthropic/claude-3.5-sonnet"],
    },
    "mistral": {
        "api_base_url": "https://api.mistral.ai/v1",
        "response_json_path": "choices[0].message.content",
        "models": ["mistral-large-latest", "mistral-small-latest"],
    },
    "cohere": {
        "api_base_url": "https://api.cohere.com/v1",
        "response_json_path": "text",
        "models": ["command-r-plus", "command-r"],
    },
}


def extract_json_path(data: dict, path: str) -> str:
    """Extract response text using dot-notation or JSONPath."""
    if path.startswith("response."):
        path = path.replace("response.", "", 1)
    try:
        if "[" in path:
            expr = jsonpath_parse(f"$.{path}" if not path.startswith("$") else path)
            matches = expr.find(data)
            if matches:
                val = matches[0].value
                return str(val) if val is not None else ""
        parts = path.split(".")
        current: Any = data
        for part in parts:
            if "[" in part:
                key, idx = part.split("[")
                idx = int(idx.rstrip("]"))
                current = current[key][idx]
            else:
                current = current[part]
        return str(current) if current is not None else ""
    except Exception:
        return json.dumps(data)[:2000]


class LLMClient:
    def __init__(self, connection: dict):
        self.connection = connection
        self.api_key = vault.decrypt(connection["api_key_encrypted"]) if connection.get("api_key_encrypted") else connection.get("api_key", "")

    async def complete(self, prompt: str) -> tuple[str, dict]:
        provider = self.connection["provider"].lower()
        if provider in ("openai", "groq", "deepseek", "openrouter", "mistral", "azure_openai"):
            return await self._openai_compatible(prompt)
        if provider == "claude":
            return await self._claude(prompt)
        if provider == "gemini":
            return await self._gemini(prompt)
        if provider == "ollama":
            return await self._ollama(prompt)
        if provider == "cohere":
            return await self._cohere(prompt)
        return await self._openai_compatible(prompt)

    async def _openai_compatible(self, prompt: str) -> tuple[str, dict]:
        base = self.connection["api_base_url"].rstrip("/")
        url = f"{base}/chat/completions" if "/chat" not in base else base
        if not url.endswith("/chat/completions"):
            url = f"{base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        headers.update(self.connection.get("custom_headers", {}))
        payload = {
            "model": self.connection["model_name"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.connection.get("temperature", 0.7),
            "max_tokens": self.connection.get("max_tokens", 1024),
        }
        timeout = self.connection.get("timeout_seconds", 60)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        text = extract_json_path(data, self.connection.get("response_json_path", "choices[0].message.content"))
        return text, data

    async def _claude(self, prompt: str) -> tuple[str, dict]:
        url = f"{self.connection['api_base_url'].rstrip('/')}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        headers.update(self.connection.get("custom_headers", {}))
        payload = {
            "model": self.connection["model_name"],
            "max_tokens": self.connection.get("max_tokens", 1024),
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=self.connection.get("timeout_seconds", 60)) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return extract_json_path(data, self.connection.get("response_json_path", "content[0].text")), data

    async def _gemini(self, prompt: str) -> tuple[str, dict]:
        model = self.connection["model_name"]
        url = f"{self.connection['api_base_url'].rstrip('/')}/models/{model}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return extract_json_path(data, self.connection.get("response_json_path", "candidates[0].content.parts[0].text")), data

    async def _ollama(self, prompt: str) -> tuple[str, dict]:
        url = f"{self.connection['api_base_url'].rstrip('/')}/api/chat"
        payload = {"model": self.connection["model_name"], "messages": [{"role": "user", "content": prompt}], "stream": False}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
        return extract_json_path(data, "message.content"), data

    async def _cohere(self, prompt: str) -> tuple[str, dict]:
        url = f"{self.connection['api_base_url'].rstrip('/')}/chat"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.connection["model_name"], "message": prompt}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data.get("text", ""), data

    async def health_check(self) -> tuple[bool, str]:
        try:
            text, _ = await self.complete("Reply with exactly: OK")
            return "ok" in text.lower()[:20], "healthy"
        except Exception as e:
            return False, str(e)
