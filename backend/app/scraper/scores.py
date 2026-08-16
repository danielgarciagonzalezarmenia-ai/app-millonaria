"""Cliente de la API JSON pública de 365scores.

Endpoints usados (misma familia que el /web/trends/ que usa la web):
- /web/games/    -> partidos del día
- /web/trends/   -> tendencias por partido (fuego/llama + cuotas)

Parámetros estándar que usa la propia web de 365scores.
Ruta de ejemplo facilitada por el usuario:
  /web/trends/?appTypeId=5&langId=14&timezoneName=America%2FBogota&userCountryId=109
                     &games=4750520&topBookmaker=4
"""

from __future__ import annotations

import datetime as dt
import logging

from app.models import ApiCompetitor, ApiGame, ApiTrend, TrendsResponse
from app.scraper.client import ScraperClient

logger = logging.getLogger("scraper.scores")

WEB_BASE = "https://webws.365scores.com"
COMMON_PARAMS = {
    "appTypeId": "5",
    "langId": "14",
    "timezoneName": "America/Bogota",
    "userCountryId": "109",
}

# Los partidos 'programados' (por jugar) tienen statusGroup 2 (Prog.).
SCHEDULED_STATUS = 2


class ScoresAPI:
    def __init__(self, *, top_bookmaker: int = 4, max_games: int | None = None,
                 filter_leagues: list[str] | None = None) -> None:
        self.top_bookmaker = top_bookmaker
        self.max_games = max_games
        self.filter_leagues = filter_leagues or []
        self._client = ScraperClient(base_url=WEB_BASE)

    @property
    def client(self) -> ScraperClient:
        return self._client

    def _url(self, endpoint: str, params: dict) -> str:
        from urllib.parse import urlencode

        merged = {**COMMON_PARAMS, **params}
        return f"{endpoint}?{urlencode(merged)}"

    async def fetch_games(self) -> list[ApiGame]:
        url = self._url("/web/games/", {"sports": "1"})
        data = await self._client.get_json(url)

        games = [ApiGame(**g) for g in data.get("games", []) if isinstance(g, dict)]

        # Popularidad de competición para priorizar las ligas grandes
        # (mismo criterio que usa la web para ordenar sus feeds).
        comp_pop: dict[int, int] = {}
        for c in data.get("competitions", []):
            if isinstance(c, dict) and c.get("id"):
                comp_pop[c["id"]] = c.get("popularityRank", 0)
        games.sort(
            key=lambda g: (comp_pop.get(g.competitionId or -1, 0), g.startTime),
            reverse=True,
        )

        upcoming = [g for g in games if g.statusGroup == SCHEDULED_STATUS]

        if self.filter_leagues:
            wanted = {n.lower() for n in self.filter_leagues}
            upcoming = [
                g for g in upcoming
                if g.competitionDisplayName.lower() in wanted
            ]

        if self.max_games:
            upcoming = upcoming[: self.max_games]

        logger.info(
            "Partidos del día: %d | programados: %d | a analizar: %d",
            len(games),
            len([g for g in games if g.statusGroup == SCHEDULED_STATUS]),
            len(upcoming),
        )
        return upcoming

    async def fetch_trends(self, game_id: int) -> TrendsResponse:
        url = self._url(
            "/web/trends/",
            {
                "games": str(game_id),
                "topBookmaker": str(self.top_bookmaker),
            },
        )
        data = await self._client.get_json(url)
        return TrendsResponse(**data)

    async def fetch_all_trends(self, games: list[ApiGame]) -> list[tuple[ApiGame, TrendsResponse]]:
        results: list[tuple[ApiGame, TrendsResponse]] = []
        for game in games:
            try:
                trends = await self.fetch_trends(game.id)
                results.append((game, trends))
            except Exception:
                logger.exception("Fallo al obtener tendencias del partido %s (%s vs %s)",
                                 game.id, game.homeCompetitor.name if game.homeCompetitor else "?",
                                 game.awayCompetitor.name if game.awayCompetitor else "?")
        return results

    @staticmethod
    def competitor_name(comp: ApiCompetitor | None) -> str:
        return comp.name if comp else ""


def parse_datetime(value: str) -> dt.datetime | None:
    if not value:
        return None
    try:
        # startTime incluye offset: "2026-08-16T10:00:00-05:00"
        parsed = dt.datetime.fromisoformat(value)
        return parsed.astimezone(dt.timezone.utc)
    except ValueError:
        return None