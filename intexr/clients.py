"""Minimal LLM clients (stdlib only) with an on-disk response cache, rate limiting, and free-tier presets.

Spec format: "<provider>:<model>". Providers:
  groq        free tier   https://console.groq.com          GROQ_API_KEY
  gemini      free tier   https://aistudio.google.com       GEMINI_API_KEY   (OpenAI-compatible endpoint)
  cerebras    free tier   https://cloud.cerebras.ai         CEREBRAS_API_KEY
  openrouter  ':free' models only stay free                 OPENROUTER_API_KEY
  ollama      local, free (http://localhost:11434)          no key
  vllm        your own server, e.g. on Kaggle/Colab GPUs    VLLM_BASE_URL (+ optional VLLM_API_KEY)
  openai      any OpenAI-compatible endpoint                OPENAI_BASE_URL, OPENAI_API_KEY
  anthropic   paid                                          ANTHROPIC_API_KEY
List a provider's model ids with:  python3 scripts/list_models.py groq

Free tiers have per-minute and per-day caps. Set requests-per-minute with INTEXR_RPM (default 20 for
free providers). Every response is cached in results/.cache, so when a daily cap is hit the run stops
with a clear message and simply re-running the same command tomorrow resumes where it left off.

DATA NOTE: free tiers may log or train on prompts (check each provider's terms). Use them only on
public data (MEDEC, IU X-ray, COCO, VitaminC, EditPropBench). NEVER send MIMIC text to a free tier;
PhysioNet's rules: https://physionet.org/news/post/llm-responsible-use/
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "results", ".cache")

PRESETS = {  # provider -> (base url, api-key env var or None, free?)
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY", True),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY", True),
    "cerebras": ("https://api.cerebras.ai/v1", "CEREBRAS_API_KEY", True),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", True),
    "ollama": ("http://localhost:11434/v1", None, True),
}


class QuotaExhausted(RuntimeError):
    """Raised when a provider keeps returning 429; cached work is kept, re-run later to resume."""


def _post(url, headers, body, retries=6):
    data = json.dumps(body).encode()
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read()[:500]
            if e.code == 429:
                if attempt == retries - 1:
                    raise QuotaExhausted(f"{url}: rate/daily limit reached ({msg!r}). Cached results are saved; "
                                         "re-run the same command later to resume.")
                wait = float(e.headers.get("retry-after") or 0) or min(120, 10 * 2 ** attempt)
                time.sleep(min(wait, 300))
                continue
            if e.code in (500, 502, 503, 529) and attempt < retries - 1:
                time.sleep(2 ** attempt * 5)
                continue
            raise RuntimeError(f"{url} -> HTTP {e.code}: {msg!r}")
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(5)
                continue
            raise RuntimeError(f"{url}: cannot connect ({e.reason}). Is the server running?")


class Client:
    def __init__(self, spec, temperature=0.0, max_tokens=4000):
        self.provider, self.model = spec.split(":", 1)
        self.temperature, self.max_tokens = temperature, max_tokens
        if self.provider not in PRESETS and self.provider not in ("anthropic", "openai", "vllm"):
            raise ValueError(f"unknown provider in {spec}; choose from {sorted(PRESETS) + ['anthropic', 'openai', 'vllm']}")
        free = PRESETS.get(self.provider, (None, None, self.provider == "vllm"))[2]
        local = self.provider in ("ollama", "vllm")
        rpm = float(os.environ.get("INTEXR_RPM", "20" if free and not local else "0"))
        self.min_interval = 60.0 / rpm if rpm > 0 else 0.0
        self._last = 0.0

    def endpoint(self):
        if self.provider in PRESETS:
            base, env, _ = PRESETS[self.provider]
            if env and not os.environ.get(env):
                raise RuntimeError(f"set {env} (free key from the provider's console)")
            return base, os.environ.get(env, "none") if env else "none"
        if self.provider == "vllm":
            return os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1"), os.environ.get("VLLM_API_KEY", "none")
        return os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"), os.environ.get("OPENAI_API_KEY", "none")

    def __call__(self, system, messages):
        key = hashlib.sha256(json.dumps([self.provider, self.model, self.temperature, system, messages] + ([os.environ["INTEXR_EXTRA_BODY"]] if os.environ.get("INTEXR_EXTRA_BODY") else [])).encode()).hexdigest()
        path = os.path.join(CACHE_DIR, key + ".json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)["text"]
        wait = self.min_interval - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()
        t0 = time.time()
        text, usage = self._anthropic(system, messages) if self.provider == "anthropic" else self._openai(system, messages)
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "w") as f:
            json.dump({"text": text, "usage": usage, "latency_s": time.time() - t0, "model": self.model,
                       "provider": self.provider}, f)
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
        base, key = self.endpoint()
        msgs = ([{"role": "system", "content": system}] if system else []) + messages
        body = {"model": self.model, "messages": msgs, "max_tokens": self.max_tokens}
        if os.environ.get("OPENAI_SEND_TEMPERATURE", "1") == "1":
            body["temperature"] = self.temperature
        # extra request fields, e.g. for Qwen3 on vLLM: INTEXR_EXTRA_BODY='{"chat_template_kwargs": {"enable_thinking": false}}'
        body.update(json.loads(os.environ.get("INTEXR_EXTRA_BODY", "{}")))
        r = _post(base.rstrip("/") + "/chat/completions",
                  {"Authorization": f"Bearer {key}", "content-type": "application/json",
                   "User-Agent": "intexr-research/0.1"}, body)
        msg = r["choices"][0]["message"]
        text = msg.get("content") or ""
        # some reasoning models (e.g. gpt-oss, qwen3) wrap thinking in <think>...</think>; drop it
        if "</think>" in text:
            text = text.split("</think>", 1)[1]
        return text.strip(), r.get("usage")
