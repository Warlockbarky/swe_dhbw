"""OpenAI chat client wrapper with retry logic."""

from __future__ import annotations

import os
import time
from pathlib import Path

import requests


class ki_analyzer:
    """Controller für KI-Chat via OpenAI API.

    Konfiguration über Env Vars:
    - OPENAI_API_KEY (required)
    - OPENAI_MODEL (optional, default: gpt-4o-mini)
    - OPENAI_BASE_URL (optional, default: https://api.openai.com/v1)
    """

    def __init__(
        self,
        max_wiederholungen: int = 3,
        modell: str | None = None,
        timeout_s: float = 60.0,
    ):
        self.max_wiederholungen = int(max_wiederholungen)
        self.aktuelle_iteration = 0
        self.timeout_s = float(timeout_s)

        self._load_dotenv()
        self._api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self._base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self._modell = (modell or os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()

    def _load_dotenv(self) -> None:
        """Load dotenv values to allow local dev without external tooling.

        Returns:
            None
        """
        candidates = [Path.cwd() / ".env", Path(__file__).resolve().parents[2] / ".env"]
        for path in candidates:
            if not path.exists():
                continue
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    text = line.strip()
                    if not text or text.startswith("#"):
                        continue
                    if "=" not in text:
                        continue
                    key, value = text.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    if key and key not in os.environ:
                        os.environ[key] = value
            except OSError:
                return
            return

    def chat(self, messages: list[dict[str, str]], *, temperature: float = 0.2) -> str:
        return self._call_openai_chat_messages(messages=messages, temperature=temperature)

    def _call_openai_chat_messages(self, *, messages: list[dict[str, str]], temperature: float) -> str:
        """Send chat messages to the OpenAI API with bounded retry backoff.

        Args:
            messages (list[dict[str, str]]): Chat payload in OpenAI format.
            temperature (float): Sampling temperature for the model.

        Returns:
            str: Assistant response text.

        Raises:
            ValueError: If the API key is missing.
            RuntimeError: If the API request fails after retries.
        """
        if not self._api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please set the OPENAI_API_KEY environment variable to use the OpenAI API."
            )

        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._modell,
            "messages": messages,
            "temperature": float(temperature),
        }

        last_exc: Exception | None = None
        for attempt in range(1, max(self.max_wiederholungen, 1) + 1):
            self.aktuelle_iteration = attempt
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout_s)
                if resp.status_code >= 400:
                    raise RuntimeError(f"OpenAI API HTTP {resp.status_code}: {resp.text}")
                data = resp.json()
                return str(data["choices"][0]["message"]["content"])
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                # Exponential backoff (bounded)
                sleep_s = min(2.0 ** (attempt - 1), 8.0)
                time.sleep(sleep_s)

        raise RuntimeError(
            f"OpenAI API call failed after {self.max_wiederholungen} attempts: {last_exc}"
        )
