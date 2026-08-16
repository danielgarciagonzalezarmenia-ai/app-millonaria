"""Modelos de datos de pronósticos."""

from __future__ import annotations

import datetime as dt
from enum import Enum

from pydantic import BaseModel, Field


class TrendType(str, Enum):
    OVER_2_5 = "over_2_5"
    BTTS = "btts"  # Ambos marcan (BTTS = Both Teams To Score)
    HOME_WIN = "home_win"  # El local gana
    AWAY_WIN = "away_win"  # El visitante gana
    HOME_OR_DRAW = "home_or_draw"
    AWAY_OR_DRAW = "away_or_draw"
    OTHER = "other"


class SourceSide(str, Enum):
    FOR = "for"  # tendencia positiva / a favor
    AGAINST = "against"


class StatsTrend(BaseModel):
    """Una tendencia individual de un equipo respecto a una marca."""

    label: str
    side: SourceSide
    value: str
    fire: bool = False  # tendencia destacada (el "fuego"/llama de 360score)
    score: float = 0.0  # confianza normalizada 0..1


class MatchReport(BaseModel):
    """Resultado de extraer las estadísticas/tendencias de un partido."""

    home_team: str
    away_team: str
    kickoff: dt.datetime | None = None
    league: str = ""
    current_home_score: int | None = None
    current_away_score: int | None = None
    match_id: str
    url: str = ""
    home_trends: list[StatsTrend] = Field(default_factory=list)
    away_trends: list[StatsTrend] = Field(default_factory=list)
    head_to_head_trends: list[StatsTrend] = Field(default_factory=list)


class TrendSource(BaseModel):
    label: str
    side: SourceSide
    value: str


class Prediction(BaseModel):
    """Pronóstico publicado por la app (gratis o premium)."""

    match_id: str
    league: str
    home_team: str
    away_team: str
    kickoff: dt.datetime | None = None
    market: str  # ej: "Más de 2.5 goles", "Ambos marcan", "Gana (X2)"
    market_type: TrendType = TrendType.OTHER
    selection: str  # ej: "más_de_2.5", "ambos_marcan", "gana_o_empata_X2"
    odds: float
    confidence: float = 0.0  # 0..1
    basis: list[TrendSource] = Field(default_factory=list)
    premium: bool = False
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    status: str = "active"


class PredictionPublic(BaseModel):
    """Versión segura de publicar (no expone info interna)."""

    match_id: str
    league: str
    home_team: str
    away_team: str
    kickoff: dt.datetime | None = None
    market: str
    market_type: TrendType
    selection: str
    odds: float
    confidence: float
    basis: list[TrendSource]
    premium: bool
    created_at: dt.datetime


# ---------------------------------------------------------------------------
# Modelos de la API JSON de 365scores (endpoint /web/trends/ y /web/games/)
# ---------------------------------------------------------------------------

class OddsRate(BaseModel):
    decimal: float
    fractional: str = ""
    american: str = ""


class TrendOdds(BaseModel):
    num: int = 1
    rate: OddsRate | None = None
    bookmakerId: int = 0


class ApiTrend(BaseModel):
    """Una tendencia tal y como la devuelve 365scores."""

    id: int
    text: str = ""
    cause: str = ""
    betCTA: str = ""
    divId: int | None = None
    competitorIds: list[int] = Field(default_factory=list)
    gameId: int = 0
    odds: TrendOdds | None = None
    bookmakerId: int = 0
    confidenceTrendIds: list[int] = Field(default_factory=list)
    isGeneralGameBet: bool = False
    percentage: float = 0.0

    @property
    def is_fire(self) -> bool:
        """La 'llama' = tendencia corroborada por otra (la API las llama
        confidenceTrendIds). Es el marcador visual de fuego de la web."""
        return bool(self.confidenceTrendIds)

    @property
    def decimal_odds(self) -> float | None:
        if self.odds and self.odds.rate:
            return self.odds.rate.decimal
        return None


class ApiCompetition(BaseModel):
    id: int
    name: str = ""


class ApiCompetitor(BaseModel):
    id: int
    name: str = ""
    nameForURL: str = ""


class ApiGame(BaseModel):
    """Partido tal y como lo devuelve /web/games/."""

    id: int
    competitionId: int | None = None
    competitionDisplayName: str = ""
    startTime: str = ""
    statusGroup: int = 0
    statusText: str = ""
    homeCompetitor: ApiCompetitor | None = None
    awayCompetitor: ApiCompetitor | None = None


class TrendsResponse(BaseModel):
    trends: list[ApiTrend] = Field(default_factory=list)
    competitors: list[ApiCompetitor] = Field(default_factory=list)
    competitions: list[ApiCompetition] = Field(default_factory=list)