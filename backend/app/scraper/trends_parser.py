"""Interpretación de tendencias de 365scores -> pronósticos de App Millonaria.

Reglas de negocio aplicadas (las que definiste):
1. Solo tendencias con FUEGO/LLAMA  -> field `confidenceTrendIds` poblado.
2. Solo POSITIVAS -> usamos la formulación de apuesta (`betCTA`/`cause`) si ya
   es el mercado a favor (ej: "Villarreal no ganó" se traduce a "Racing gana o
   empata").
3. Solo mercados que INVOLUCRAN A AMBOS EQUIPOS:
   - Ambos equipos marcan (BTTS)
   - Más de 2.5 goles
   - Victoria de X (X gana)
   - X gana o empata / doble oportunidad (1X / X2)
   (se descartan: anotó primero, primer tiempo, menos de 2.5, córners, etc.)
4. Cuota >= 1.70.
"""

from __future__ import annotations

import re
import unicodedata

from app.models import (
    ApiGame,
    Prediction,
    TrendSource,
    TrendType,
    TrendsResponse,
)
from app.core.config import settings
from app.scraper.scores import parse_datetime


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower().strip()


# --- Clasificación de mercado a partir del texto APOSTABLE (positivo) ---

class _MarketMatch:
    __slots__ = ("market", "kind")

    def __init__(self, market: TrendType, kind: str) -> None:
        self.market = market
        self.kind = kind  # "btts" | "over" | "dc" | "win"


DOUBLE_CHANCE_RE = re.compile(r"(gan[ao]r?|empata|empate) (o|y) (empata|empatar|gan[ao])")
EDGE_MARKET_R = re.compile(
    r"primero\s|primer\s|segundo tiempo|primer tiempo|anot[óo]|marco|tarjeta|c[óo]rner|menos de|corners|tarjetas|pose",
    re.I,
)


def classify_market(positive_text: str) -> _MarketMatch | None:
    """Devuelve el mercado si el texto apostable encaja en nuestros mercados."""
    t = _norm(positive_text)
    if not t or len(t) > 100:
        return None

    # Fuera: mercados de borde (tiempos, cómers, tarjetas, under).
    if EDGE_MARKET_R.search(t):
        return None

    if "ambos equipos marcaron" in t or "ambos marcan" in t or "ambos equipos marcaran" in t:
        return _MarketMatch(TrendType.BTTS, "btts")

    if "mas de 2.5" in t or "mas de 2,5" in t:
        return _MarketMatch(TrendType.OVER_2_5, "over")

    if "gana o empata" in t or "gano o empato" in t or DOUBLE_CHANCE_RE.search(t):
        return _MarketMatch(TrendType.HOME_OR_DRAW, "dc")  # side se define después

    if re.search(r"victoria de|vence\b|vencio\b|gan[oó]\b|ganarael|ganar[áa] el", t):
        return _MarketMatch(TrendType.HOME_WIN, "win")

    return None


def _side_of_text(positive_text: str, game: ApiGame) -> str | None:
    """Resuelve si el mercado favorece al local o visitante mirando el nombre
    del equipo en el texto; si no, usa competitorIds."""
    t = _norm(positive_text)
    pairs = []
    if game.homeCompetitor:
        pairs.append((game.homeCompetitor.name, game.homeCompetitor.nameForURL, "home"))
    if game.awayCompetitor:
        pairs.append((game.awayCompetitor.name, game.awayCompetitor.nameForURL, "away"))

    for name, name_for_url, side in pairs:
        name_n = _norm(name)
        if name_n and len(name_n) >= 3 and name_n in t:
            return side
        sym = _norm(name_for_url or "")
        if sym and sym in t:
            return side
    return None


def _market_label(market: TrendType, side: str | None) -> str:
    if market in (TrendType.BTTS,):
        return "Ambos marcan"
    if market == TrendType.OVER_2_5:
        return "Más de 2.5 goles"
    if market in (TrendType.HOME_OR_DRAW, TrendType.AWAY_OR_DRAW):
        return (
            "Local gana o empata (1X)"
            if market == TrendType.HOME_OR_DRAW
            else "Visitante gana o empata (X2)"
        )
    if market in (TrendType.HOME_WIN, TrendType.AWAY_WIN):
        return "Gana el local" if market == TrendType.HOME_WIN else "Gana el visitante"
    return market.value


def _selection(market: TrendType, side: str | None) -> str:
    if market == TrendType.BTTS:
        return "ambos_marcan"
    if market == TrendType.OVER_2_5:
        return "mas_de_2_5"
    if market in (TrendType.HOME_OR_DRAW, TrendType.AWAY_OR_DRAW):
        return "local_gana_o_empata" if market == TrendType.HOME_OR_DRAW else "visitante_gana_o_empata"
    if market in (TrendType.HOME_WIN, TrendType.AWAY_WIN):
        return "local_gana" if market == TrendType.HOME_WIN else "visitante_gana"
    return "other"


# --- Generación de predicciones ---

def _positive_text(trend) -> str:
    """Formulación apostable: preferimos betCTA (ya en positivo); si está vacío
    usamos la causa. Si la causa es negativa ("no ganó") y el betCTA la ha
    traducido, ese es el texto positivo."""
    bet = trend.betCTA or trend.cause or trend.text
    return bet


def build_predictions(game: ApiGame, trends_resp: TrendsResponse) -> list[Prediction]:
    # candidates[clave] -> mejor Prediction para ese mercado/lado
    candidates: dict[tuple[str, str], Prediction] = {}

    for trend in trends_resp.trends:
        if not trend.is_fire:
            continue  # 1) solo tendencias con llama/fuego

        odds = trend.decimal_odds
        if odds is None or odds < settings.min_odds:
            continue  # 4) cuota minima 1.70

        positive = _positive_text(trend)
        match_info = classify_market(positive)
        if match_info is None:
            continue  # 3) solo mercados globales

        side = _side_of_text(positive, game) or _side_from_competitor_ids(trend, game)
        if match_info.kind in ("dc", "win") and side is None:
            continue  # win / doble oportunidad necesitan saber el lado

        if match_info.kind == "win":
            market_type = TrendType.HOME_WIN if side == "home" else TrendType.AWAY_WIN
        elif match_info.kind == "dc":
            market_type = TrendType.HOME_OR_DRAW if side == "home" else TrendType.AWAY_OR_DRAW
        else:
            market_type = match_info.market

        # Dedupe: en mercados genéricos (btts/over) el lado no cuenta.
        key: tuple[str, str] = (
            (market_type.value, "")
            if match_info.kind in ("btts", "over")
            else (market_type.value, side or "")
        )

        confidence = round(min(trend.percentage, 1.0), 3)
        existing = candidates.get(key)
        if existing and existing.confidence >= confidence:
            continue  # ya tenemos una mejor para este mercado

        candidates[key] = Prediction(
            match_id=str(game.id),
            league=game.competitionDisplayName or "",
            home_team=game.homeCompetitor.name if game.homeCompetitor else "",
            away_team=game.awayCompetitor.name if game.awayCompetitor else "",
            kickoff=parse_datetime(game.startTime),
            market=_market_label(market_type, side),
            market_type=market_type,
            selection=_selection(market_type, side),
            odds=round(odds, 2),
            confidence=confidence,
            basis=[
                TrendSource(
                    label=trend.cause or trend.text,
                    side="for",
                    value=trend.text,
                )
            ],
            premium=_is_premium(game, market_type),
        )

    predictions = sorted(candidates.values(), key=lambda p: (-p.odds, -p.confidence))
    return predictions


def _side_from_competitor_ids(trend, game: ApiGame) -> str | None:
    ids = set(trend.competitorIds)
    home_id = game.homeCompetitor.id if game.homeCompetitor else None
    away_id = game.awayCompetitor.id if game.awayCompetitor else None
    if home_id not in (None,) and home_id in ids:
        return "home"
    if away_id not in (None,) and away_id in ids:
        return "away"
    return None


def _is_premium(game: ApiGame, market_type: TrendType) -> bool:
    premium_leagues = settings.premium_leagues
    if game.competitionDisplayName in premium_leagues:
        return True
    # Regla por defecto: BTTS/Over pueden ir en la sección gratis según
    # configuración futura. Por ahora todo es gratis salvo ligas configuradas.
    return False