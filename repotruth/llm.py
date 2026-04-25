import json
import os
import urllib.error
import urllib.request
from dotenv import load_dotenv

load_dotenv()


class LLMError(RuntimeError):
    pass


class LLMClient:
    """Минимальный OpenAI-compatible client."""

    def __init__(self):
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL")

    @property
    def available(self):
        return bool(self.base_url and self.api_key and self.model)

    def complete_json(self, system_prompt, user_payload):
        if not self.available:
            raise LLMError("Задай OPENAI_BASE_URL, OPENAI_API_KEY и OPENAI_MODEL.")

        request = urllib.request.Request(
            chat_url(self.base_url),
            data=json.dumps(
                {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "Всегда отвечай на русском языке. " + system_prompt},
                        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                    ],
                }
            ).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise LLMError(f"LLM HTTP {error.code}: {body}") from error
        except urllib.error.URLError as error:
            raise LLMError(f"LLM недоступна: {error}") from error

        content = json.loads(raw)["choices"][0]["message"]["content"]
        return extract_json(content)


def chat_url(base_url):
    clean = base_url.rstrip("/")
    if clean.endswith("/chat/completions"):
        return clean
    return f"{clean}/chat/completions"


def extract_json(text):
    """Достает JSON из ответа модели.

    Важно: сначала ищем объект `{...}`. Иначе можно случайно схватить первый
    список внутри ответа вместо полного JSON-объекта.
    """

    clean = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    decoder = json.JSONDecoder()

    for target in "{[":
        for index, char in enumerate(clean):
            if char != target:
                continue
            try:
                value, _ = decoder.raw_decode(clean[index:])
                return value
            except json.JSONDecodeError:
                pass
    raise LLMError(f"LLM вернула не JSON: {text[:300]}")
