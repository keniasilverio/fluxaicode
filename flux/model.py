"""Talk to a locally running Ollama server; no paid API is required."""
import json
from urllib.request import Request, urlopen
from urllib.error import URLError


class LocalModelError(RuntimeError):
    pass


def ask_ollama(prompt: str, *, model: str, endpoint: str = "http://127.0.0.1:11434", timeout: int = 180) -> str:
    if endpoint.rstrip("/") not in {"http://127.0.0.1:11434", "http://localhost:11434"}:
        raise LocalModelError("For the first version, only local Ollama is allowed")
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.1}}).encode()
    request = Request(endpoint.rstrip("/") + "/api/generate", data=payload,
                      headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read())
        return str(data["response"])
    except (URLError, KeyError, ValueError, TimeoutError) as exc:
        raise LocalModelError(f"Ollama unavailable or invalid response: {exc}") from exc
