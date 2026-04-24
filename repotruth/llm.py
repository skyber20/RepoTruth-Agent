import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


class LLMError(RuntimeError):
    """Ошибка ответа модели."""


@dataclass
class LLMClient:
    """Клиент для OpenAI-compatible Qwen API."""

    base_url: str | None = None
    api_key: str | None = None
    model: str | None = None
    timeout: int = 90
    temperature: float = 0.1

    @classmethod
    def from_env(cls):
        return cls(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("MODEL_DEFAULT"),
            timeout=int(os.getenv("REPOTRUTH_LLM_TIMEOUT", "90")),
        )

    @property
    def available(self):
        return bool(self.base_url and self.api_key and self.model)

    def complete_json(self, system_prompt, user_payload):
        if not self.available:
            raise LLMError("Нужны OPENAI_BASE_URL, OPENAI_API_KEY и OPENAI_MODEL.")

        answer = self._complete(system_prompt, user_payload)
        return extract_json(answer)

    def try_complete_json(self, system_prompt, user_payload):
        try:
            return self.complete_json(system_prompt, user_payload)
        except Exception:
            return None

    def _complete(self, system_prompt, user_payload):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, indent=2)},
            ],
            "temperature": self.temperature,
        }
        request = urllib.request.Request(
            chat_url(self.base_url),
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise LLMError(f"LLM HTTP {error.code}: {body}") from error
        except urllib.error.URLError as error:
            raise LLMError(f"LLM недоступна: {error}") from error

        data = json.loads(raw)
        return data["choices"][0]["message"]["content"]


def chat_url(base_url):
    """Собирает URL chat/completions."""

    clean = (base_url or "").rstrip("/")
    if clean.endswith("/chat/completions"):
        return clean
    return f"{clean}/chat/completions"


def extract_json(text):
    """Достает первый JSON из ответа модели."""

    clean = text.strip()
    if clean.startswith("```"):
        clean = clean.strip("`").strip()
        if clean.lower().startswith("json"):
            clean = clean[4:].strip()

    decoder = json.JSONDecoder()
    for index, char in enumerate(clean):
        if char not in "[{":
            continue
        try:
            value, _ = decoder.raw_decode(clean[index:])
            return value
        except json.JSONDecodeError:
            pass

    raise LLMError(f"Не удалось прочитать JSON из ответа: {text[:300]}")
