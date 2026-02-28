from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable

import requests


@dataclass
class PNCPClient:
    base_url: str
    timeout_seconds: int = 30
    max_retries: int = 3
    backoff_seconds: float = 1.5

    def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(self.base_url, params=params, timeout=self.timeout_seconds)
                response.raise_for_status()
                return response.json()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(self.backoff_seconds * attempt)
        raise RuntimeError(f"PNCP request failed after {self.max_retries} attempts") from last_error

    @staticmethod
    def _extract_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
        for key in ("data", "items", "resultado", "results"):
            val = payload.get(key)
            if isinstance(val, list):
                return [v for v in val if isinstance(v, dict)]
        if isinstance(payload, list):
            return [v for v in payload if isinstance(v, dict)]
        return []

    def iterate_contracts(
        self,
        start_date: date,
        end_date: date,
        page_size: int,
        max_pages: int,
    ) -> Iterable[tuple[int, list[dict[str, Any]], dict[str, Any]]]:
        for page in range(1, max_pages + 1):
            params = {
                "dataInicial": start_date.isoformat(),
                "dataFinal": end_date.isoformat(),
                "pagina": page,
                "tamanhoPagina": page_size,
            }
            payload = self._request(params)
            items = self._extract_items(payload)
            if not items:
                break
            yield page, items, payload
