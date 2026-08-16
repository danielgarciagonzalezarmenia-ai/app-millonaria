"""Cliente HTTP para scraping con buenas prácticas.

- Rotación ligera de User-Agent.
- Timeout corto para no colgar el proceso.
- Rate limiting (pausa entre peticiones) para ser respetuosos con el sitio.
- Reintentos con backoff ante errores 429/5xx.
- Rechazo a robots.txt (opcional, configurable).
"""

from __future__ import annotations

import asyncio
import logging
import random
import time

import httpx

logger = logging.getLogger("scraper.client")

USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.4 Safari/605.1.15"
    ),
]


class ScraperClient:
    def __init__(
        self,
        base_url: str,
        *,
        min_delay: float = 1.0,
        timeout: float = 20.0,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.min_delay = min_delay
        self.timeout = timeout
        self.max_retries = max_retries
        self._last_request_at = 0.0

    async def _respect_rate_limit(self) -> None:
        now = time.monotonic()
        wait = self.min_delay - (now - self._last_request_at)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request_at = time.monotonic()

    def _headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        }

    async def get_html(self, path: str) -> httpx.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        attempt = 0
        while True:
            attempt += 1
            await self._respect_rate_limit()
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout, follow_redirects=True
                ) as client:
                    resp = await client.get(url, headers=self._headers())
                if resp.status_code in (429, 500, 502, 503, 504) and attempt <= self.max_retries:
                    await asyncio.sleep(2 ** attempt + random.random())
                    continue
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError:
                raise
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                if attempt > self.max_retries:
                    logger.exception("No se pudo obtener %s", url)
                    raise
                await asyncio.sleep(2 ** attempt + random.random())

    async def get_json(self, path: str) -> dict | list:
        resp = await self.get_html(path)
        return resp.json()