from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable

import requests

from model.bewertung import bewertung
from model.fehlerprotokoll import fehlerprotokoll
from model.zusammenfassung import zusammenfassung

if TYPE_CHECKING:
	from model.moodle_api import moodle_api


@dataclass(frozen=True)
class analyse_ergebnis:
	"""Ergebnis einer Analyse für ein Skript."""

	name: str
	quelle: str
	zusammenfassung: zusammenfassung
	bewertung: bewertung
	rohantwort: str | None = None


class ki_analyzer:
	"""Controller für KI-Analyse.

	UML (MVC):
	- Attribute: max_wiederholungen:int, aktuelle_iteration:int
	- Methoden: analyse_skripte(), bewerte_zusammenfassung(), exportiere_ergebnisse()

	LLM: OpenAI API via HTTPS (requests).
	Konfiguration über Env Vars:
	- OPENAI_API_KEY (required)
	- OPENAI_MODEL (optional, default: gpt-4o-mini)
	- OPENAI_BASE_URL (optional, default: https://api.openai.com/v1)
	"""

	def __init__(
		self,
		moodle_api: "moodle_api | None" = None,
		max_wiederholungen: int = 3,
		modell: str | None = None,
		schwellwert: float = 0.6,
		timeout_s: float = 60.0,
	):
		# moodle_api currently pulls an external dependency (`moodle`) which may not
		# be installed in all environments. We therefore keep it optional/lazy.
		self.moodle_api = moodle_api
		self.max_wiederholungen = int(max_wiederholungen)
		self.aktuelle_iteration = 0
		self.schwellwert = float(schwellwert)
		self.timeout_s = float(timeout_s)

		self._load_dotenv()
		self._api_key = os.getenv("OPENAI_API_KEY", "").strip()
		self._base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
		self._modell = (modell or os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()

		self._fehlerprotokoll = fehlerprotokoll(datum=datetime.now())

	def _load_dotenv(self) -> None:
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

	def analyse_skripte(
		self,
		skripte: Any | None = None,
		*,
		prompt_sprache: str = "de",
	) -> list[analyse_ergebnis]:
		"""Analysiert Skripte und liefert eine Liste von Ergebnissen.

		Akzeptierte Input-Formate:
		- None: versucht Daten via moodle_api zu holen (falls implementiert)
		- Iterable[str|Path]: Dateipfade
		- Iterable[tuple[name, content]]
		- Iterable[dict] mit Keys wie name/content/path
		"""

		if skripte is None:
			# moodle_api ist derzeit ein Stub; wir versuchen es trotzdem.
			try:
				api = self.moodle_api
				if api is None:
					from model.moodle_api import moodle_api  # local import (lazy)
					api = moodle_api()
					self.moodle_api = api
				skripte = api.hole_dateien()
			except Exception as exc:  # noqa: BLE001
				self._fehlerprotokoll.hinzufuegen(
					f"moodle_api.hole_dateien() fehlgeschlagen: {exc}"
				)
				skripte = []

		normalisiert = self._normalisiere_skripte(skripte)
		ergebnisse: list[analyse_ergebnis] = []

		for idx, item in enumerate(normalisiert, start=1):
			zus_text, score, kriterien, warnings, roh = self._llm_analyse(
				name=item.name,
				content=item.content,
				prompt_sprache=prompt_sprache,
			)

			zus = zusammenfassung(id=idx, inhalt=zus_text)
			bew = bewertung(score=score, kriterium_liste=kriterien, schwellwert=self.schwellwert)
			for w in warnings:
				self._fehlerprotokoll.hinzufuegen(f"{item.name}: {w}")

			ergebnisse.append(
				analyse_ergebnis(
					name=item.name,
					quelle=item.source,
					zusammenfassung=zus,
					bewertung=bew,
					rohantwort=roh,
				)
			)

		return ergebnisse

	def bewerte_zusammenfassung(
		self,
		zusammenfassung: zusammenfassung,
		*,
		prompt_sprache: str = "de",
	) -> bewertung:
		"""Bewertet eine bestehende Zusammenfassung per LLM (0..1)."""
		name = f"Zusammenfassung#{zusammenfassung.id}"
		content = zusammenfassung.inhalt
		_, score, kriterien, warnings, _ = self._llm_bewertung(
			name=name,
			content=content,
			prompt_sprache=prompt_sprache,
		)
		for w in warnings:
			self._fehlerprotokoll.hinzufuegen(f"{name}: {w}")
		return bewertung(score=score, kriterium_liste=kriterien, schwellwert=self.schwellwert)

	def exportiere_ergebnisse(
		self,
		ergebnisse: Iterable[analyse_ergebnis],
		ziel_pfad: str | Path = "ki_analyse_ergebnisse.json",
		*,
		fehlerprotokoll_pfad: str | Path = "fehlerprotokoll.txt",
	) -> Path:
		"""Exportiert Ergebnisse als JSON und schreibt optional ein Fehlerprotokoll."""
		ziel = Path(ziel_pfad)
		ziel.parent.mkdir(parents=True, exist_ok=True)

		payload = {
			"created_at": datetime.now().isoformat(timespec="seconds"),
			"model": self._modell,
			"schwellwert": self.schwellwert,
			"results": [
				{
					"name": e.name,
					"source": e.quelle,
					"summary": e.zusammenfassung.inhalt,
					"summary_length": e.zusammenfassung.laenge,
					"score": e.bewertung.score,
					"is_over_threshold": e.bewertung.ist_ueber_schwellwert(),
					"criteria": e.bewertung.kriterium_liste,
				}
				for e in ergebnisse
			],
		}

		ziel.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
		self._fehlerprotokoll.speichern(fehlerprotokoll_pfad)
		return ziel

	# -----------------
	# Internals
	# -----------------

	@dataclass(frozen=True)
	class _skript_item:
		name: str
		content: str
		source: str

	def _normalisiere_skripte(self, skripte: Any) -> list[_skript_item]:
		if skripte is None:
			return []

		# Strings / Path single
		if isinstance(skripte, (str, Path)):
			skripte = [skripte]

		items: list[ki_analyzer._skript_item] = []
		for obj in skripte:
			if isinstance(obj, (str, Path)):
				p = Path(obj).expanduser()
				text = p.read_text(encoding="utf-8", errors="replace")
				items.append(self._SkriptItem(name=p.name, content=text, source=str(p)))
				continue

			if isinstance(obj, tuple) and len(obj) == 2:
				name, content = obj
				items.append(self._SkriptItem(name=str(name), content=str(content), source="in-memory"))
				continue

			if isinstance(obj, dict):
				name = str(obj.get("name") or obj.get("titel") or obj.get("filename") or "skript")
				if "content" in obj or "inhalt" in obj or "text" in obj:
					content = str(obj.get("content") or obj.get("inhalt") or obj.get("text") or "")
					items.append(self._SkriptItem(name=name, content=content, source="dict"))
					continue
				if "path" in obj or "pfad" in obj:
					p = Path(obj.get("path") or obj.get("pfad")).expanduser()
					text = p.read_text(encoding="utf-8", errors="replace")
					items.append(self._SkriptItem(name=name or p.name, content=text, source=str(p)))
					continue

			# Fallback: repr
			items.append(self._SkriptItem(name="skript", content=str(obj), source=type(obj).__name__))

		return items

	def _llm_analyse(
		self,
		*,
		name: str,
		content: str,
		prompt_sprache: str,
	) -> tuple[str, float, list[str], list[str], str | None]:
		"""Return: (summary, score, criteria, warnings, raw_text)."""
		sys_prompt = self._system_prompt(prompt_sprache)
		user_prompt = (
			"Analysiere das folgende Skript und liefere eine kompakte Zusammenfassung und eine Bewertung.\n\n"
			"Gib AUSSCHLIESSLICH JSON zurück (keine Markdown-Zäune).\n"
			"Schema:\n"
			"{\n"
			"  \"summary\": string,\n"
			"  \"score\": number,  // 0..1\n"
			"  \"criteria\": string[],\n"
			"  \"warnings\": string[]\n"
			"}\n\n"
			f"Skriptname: {name}\n\n"
			"--- BEGIN SCRIPT ---\n"
			f"{content}\n"
			"--- END SCRIPT ---\n"
		)

		raw = self._call_openai_chat(system=sys_prompt, user=user_prompt)
		data, warnings = self._parse_json_response(raw)

		summary = str(data.get("summary") or "")
		score = self._clamp_score(data.get("score"))
		criteria = self._ensure_str_list(data.get("criteria"))
		warnings.extend(self._ensure_str_list(data.get("warnings")))
		return summary, score, criteria, warnings, raw

	def _llm_bewertung(
		self,
		*,
		name: str,
		content: str,
		prompt_sprache: str,
	) -> tuple[str, float, list[str], list[str], str | None]:
		sys_prompt = self._system_prompt(prompt_sprache)
		user_prompt = (
			"Bewerte die folgende Zusammenfassung auf Qualität und Vollständigkeit.\n\n"
			"Gib AUSSCHLIESSLICH JSON zurück (keine Markdown-Zäune).\n"
			"Schema:\n"
			"{\n"
			"  \"score\": number,  // 0..1\n"
			"  \"criteria\": string[],\n"
			"  \"warnings\": string[]\n"
			"}\n\n"
			f"Name: {name}\n\n"
			"--- BEGIN SUMMARY ---\n"
			f"{content}\n"
			"--- END SUMMARY ---\n"
		)

		raw = self._call_openai_chat(system=sys_prompt, user=user_prompt)
		data, warnings = self._parse_json_response(raw)
		score = self._clamp_score(data.get("score"))
		criteria = self._ensure_str_list(data.get("criteria"))
		warnings.extend(self._ensure_str_list(data.get("warnings")))
		return "", score, criteria, warnings, raw

	def _system_prompt(self, sprache: str) -> str:
		if sprache.lower().startswith("en"):
			return "You are a strict analysis assistant. Always return valid JSON only (no Markdown)."
		return "Du bist ein strenger Analyse-Assistent. Gib immer nur valides JSON ohne Markdown zurück."

	def chat(self, messages: list[dict[str, str]], *, temperature: float = 0.2) -> str:
		return self._call_openai_chat_messages(messages=messages, temperature=temperature)

	def _call_openai_chat(self, *, system: str, user: str) -> str:
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
			"messages": [
				{"role": "system", "content": system},
				{"role": "user", "content": user},
			],
			"temperature": 1,
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

	def _call_openai_chat_messages(self, *, messages: list[dict[str, str]], temperature: float) -> str:
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

	def _parse_json_response(self, raw_text: str) -> tuple[dict[str, Any], list[str]]:
		warnings: list[str] = []
		text = raw_text.strip()

		# Fast path
		try:
			return json.loads(text), warnings
		except Exception:  # noqa: BLE001
			pass

		# Try to extract a JSON object using the first/last curly brace.
		start = text.find("{")
		end = text.rfind("}")
		if start == -1 or end == -1 or end <= start:
			warnings.append("LLM did not return JSON (no curly braces found).")
			return {}, warnings

		candidate = text[start : end + 1]
		try:
			return json.loads(candidate), warnings
		except Exception as exc:  # noqa: BLE001
			warnings.append(f"Failed to parse JSON from the LLM response: {exc}")
			return {}, warnings

	@staticmethod
	def _clamp_score(value: Any) -> float:
		try:
			score = float(value)
		except Exception:  # noqa: BLE001
			return 0.0
		return max(0.0, min(1.0, score))

	@staticmethod
	def _ensure_str_list(value: Any) -> list[str]:
		if value is None:
			return []
		if isinstance(value, list):
			out: list[str] = []
			for x in value:
				if x is None:
					continue
				out.append(str(x))
			return out
		return [str(value)]
