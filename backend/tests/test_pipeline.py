"""Pruebas de la lógica de negocio del parser de tendencias.

Ejecutar:
  pytest backend/tests -v          (o)  python backend/tests/test_pipeline.py
"""

from __future__ import annotations

import json
import pathlib

from app.models import ApiGame, ApiCompetitor, Prediction, TrendSource, TrendsResponse
from app.scraper.trends_parser import build_predictions, classify_market, _norm
from app.scraper.pipeline import apply_daily_free_policy, calculate_free_count

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "trends_4750520.json"


def load_trends(filename: str = "trends_4750520.json") -> TrendsResponse:
    with open(FIXTURE.with_name(filename), encoding="utf-8") as fh:
        return TrendsResponse(**json.load(fh))


def make_game() -> ApiGame:
    return ApiGame(
        id=4750520,
        competitionId=11,
        competitionDisplayName="LaLiga",
        startTime="2026-08-16T10:00:00-05:00",
        statusGroup=2,
        homeCompetitor=ApiCompetitor(id=137, name="Racing de Santander", nameForURL="racing-santander"),
        awayCompetitor=ApiCompetitor(id=133, name="Villarreal CF", nameForURL="villarreal"),
    )


def test_classify_market_cases():
    assert classify_market("Ambos equipos marcarán").market.value == "btts"
    assert classify_market("Más de 2.5 goles").market.value == "over_2_5"
    assert classify_market("Racing gana o empata").market.value == "home_or_draw"
    assert classify_market("Victoria de Racing").market.value == "home_win"

    # Mercados excluidos por la regla de negocio
    assert classify_market("Villarreal anotará primero") is None
    assert classify_market("Menos de 2.5 goles como visitante") is None
    assert classify_market("Racing perdió el primer tiempo de visitante") is None


def test_fire_detection_sample():
    trends = load_trends()
    fire = [t for t in trends.trends if t.is_fire]
    causes = sorted(t.cause for t in fire)
    assert "Ambos equipos marcaron" in causes
    assert "Racing ganó" in causes


def test_sample_game_predictions():
    game = make_game()
    trends = load_trends()
    preds = build_predictions(game, trends)

    # En el partido de ejemplo, solo debe aparecer la victoria de Racing
    # (las de BTTS/over quedan fuera por cuota < 1.70, y las demás no son fuego).
    assert len(preds) == 1
    assert preds[0].selection == "local_gana"
    assert preds[0].odds >= 1.70
    assert preds[0].home_team == "Racing de Santander"
    assert preds[0].away_team == "Villarreal CF"


def test_norm_strips_accents():
    assert _norm("Más de 2.5 goles") == "mas de 2.5 goles"


def test_daily_free_policy_few_gives_one_free():
    # Con pocos pronósticos (por debajo del umbral) se regala 1.
    assert calculate_free_count(3) == 1
    preds = [make_pred(confidence=1.0, odds=2.0, i=i) for i in range(3)]
    out = apply_daily_free_policy(preds)
    free = [p for p in out if not p.premium]
    assert len(free) == 1
    # El gratis es el de mayor confianza (más sólido).
    assert free[0].confidence == 1.0


def test_daily_free_policy_many_gives_two_free():
    # Con bastantes pronósticos se regalan 2.
    assert calculate_free_count(7) == 2
    preds = [make_pred(confidence=0.5 + i * 0.05, odds=1.9, i=i) for i in range(7)]
    out = apply_daily_free_policy(preds)
    free = [p for p in out if not p.premium]
    assert len(free) == 2


def make_pred(*, confidence: float, odds: float, i: int) -> Prediction:
    return Prediction(
        match_id=f"m{i}",
        league="LaLiga",
        home_team=f"Equipo{i}",
        away_team=f"Rival{i}",
        market="Gana el local",
        market_type="home_win",
        selection="local_gana",
        odds=odds,
        confidence=confidence,
        basis=[TrendSource(label="x", side="for", value="x")],
        premium=False,
    )


if __name__ == "__main__":
    for name in [n for n in dir() if n.startswith("test_")]:
        fn = globals()[name]
        fn()
        print(f"OK  {name}")