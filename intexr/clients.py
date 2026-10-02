"""Minimal LLM clients (stdlib only) with an on-disk response cache.

Spec format: "anthropic:<model>" or "openai:<model>". For OpenAI-compatible servers
(vLLM, Together, Ollama), set OPENAI_BASE_URL, e.g. http://localhost:11434/v1.

MIMIC-CXR NOTE: the PhysioNet credentialed DUA forbids sending MIMIC text to services
that may retain or review it. PhysioNet lists Azure OpenAI (with human review opted out),
Amazon Bedrock, Google Vertex AI, and the Anthropic API as acceptable. Check the current
policy before running on real MIMIC data: https://physionet.org/news/post/llm-responsible-use/
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "results", ".cache")


def _post(url, headers, body, retries=4):
    data = json.dumps(body).encode()
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529) and attempt < retries - 1:
                time.sleep(2 ** attempt * 5)
                continue
            raise RuntimeError(f"{url} -> HTTP {e.code}: {e.read()[:500]!r}")


class Client:
    def __init__(self, spec, temperature=0.0, max_tokens=4000):
        self.provider, self.model = spec.split(":", 1)
        self.temperature, self.max_tokens = temperature, max_tokens
        if self.provider not in ("anthropic", "openai"):
            raise ValueError(f"unknown provider in {spec}")

    def __call__(self, system, messages):
        key = hashlib.sha256(json.dumps([self.provider, self.model, self.temperature, system, messages]).encode()).hexdigest()
        path = os.path.join(CACHE_DIR, key + ".json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)["text"]
        t0 = time.time()
        text, usage = self._anthropic(system, messages) if self.provider == "anthropic" else self._openai(system, messages)
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "w") as f:
            json.dump({"text": text, "usage": usage, "latency_s": time.time() - t0, "model": self.model}, f)
        return text

    def _anthropic(self, system, messages):
        body = {"model": self.model, "max_tokens": self.max_tokens, "messages": messages, "temperature": self.temperature}
        if system:
            body["system"] = system
        r = _post("https://api.anthropic.com/v1/messages",
                  {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}, body)
        return "".join(b.get("text", "") for b in r["content"]), r.get("usage")

    def _openai(self, system, messages):
        base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        msgs = ([{"role": "system", "content": system}] if system else []) + messages
        body = {"model": self.model, "messages": msgs}
        # Some reasoning models reject temperature; only send it for non-default endpoints or if set.
        if os.environ.get("OPENAI_SEND_TEMPERATURE", "1") == "1":
            body["temperature"] = self.temperature
        r = _post(base + "/chat/completions",
                  {"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', 'none')}",
                   "content-type": "application/json"}, body)
        return r["choices"][0]["message"]["content"], r.get("usage")
