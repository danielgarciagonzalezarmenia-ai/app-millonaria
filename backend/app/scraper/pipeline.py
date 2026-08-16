"""Pipeline de predicción contra la API JSON de 365scores.

Flujo:
1. Obtener partidos programados del día (/web/games/).
2. Por cada partido pedir sus tendencias (/web/trends/).
3. Aplicar el filtro de negocio (fuego + positivo + mercado global + cuota>=1.70)
   y generar los Prediction.
4. Publicar en Firestore.
"""

from __future__ import annotations

import datetime as dt
import logging

from app.core import firebase
from app.core.config import settings
from app.models import Prediction
from app.scraper.scores import ScoresAPI, parse_datetime
from app.scraper.trends_parser import build_predictions

logger = logging.getLogger("scraper.pipeline")

# La librería httpx loguea cada request en INFO; silenciamos para no ensuciar.
logging.getLogger("httpx").setLevel(logging.WARNING)


def calculate_free_count(total: int) -> int:
    """Cuantos gratis se regalan hoy según la cantidad de pronósticos.

    Si salen pocos (por debajo del umbral) se da 1 gratis; si salen bastantes,
    se dan 2. Las ligas premium configuradas nunca pueden ser las gratis.
    """
    if total < settings.free_predictions_threshold:
        return settings.free_predictions_when_few
    return settings.free_predictions_when_many


def apply_daily_free_policy(predictions: list[Prediction]) -> list[Prediction]:
    """Marca los mejores N pronósticos como gratis y el resto como premium.

    El mejor = mayor confianza y cuota (los más sólidos se regalan para
    mostrar valor). Devuelve una nueva lista ordenada (gratis primero)."""
    if not predictions:
        return predictions

    premium_leagues = {l.lower() for l in settings.premium_leagues}

    # Los que pertenecen a ligas premium SIEMPRE son premium (nunca entran al
    # cupo gratis del día).
    lockable = [
        p for p in predictions
        if p.league.lower() not in premium_leagues and p.basis
    ]
    forced = [p for p in predictions if p not in lockable]

    lockable.sort(key=lambda p: (-p.confidence, -p.odds))
    free_count = calculate_free_count(len(lockable))

    for i, pred in enumerate(lockable):
        pred.premium = i >= free_count

    sorted_out = sorted(lockable, key=lambda p: (p.premium, -p.confidence, -p.odds))
    return sorted_out + sorted(forced, key=lambda p: (-p.confidence, -p.odds))


class PredictionPipeline:
    def __init__(self, *, max_games: int | None = None) -> None:
        self.scores = ScoresAPI(
            max_games=max_games or settings.scraped_matches_limit,
            filter_leagues=settings.scraper_leagues,
        )

    async def collect_predictions(self) -> list[Prediction]:
        games = await self.scores.fetch_games()
        pairs = await self.scores.fetch_all_trends(games)

        predictions: list[Prediction] = []
        for game, trends in pairs:
            for pred in build_predictions(game, trends):
                predictions.append(pred)

        predictions.sort(key=lambda p: (p.kickoff or "", p.odds), reverse=True)
        predictions = apply_daily_free_policy(predictions)
        free = sum(1 for p in predictions if not p.premium)
        logger.info(
            "Generadas %d predicciones de %d partidos (%d gratis de hoy)",
            len(predictions), len(pairs), free,
        )
        return predictions

    async def publish(self, predictions: list[Prediction]) -> int:
        db = firebase.db()

        # 1) Borrar predicciones anteriores de HOY para evitar duplicados
        #    y contradicciones de runs previos. Usamos solo filtro por status
        #    (sin índice compuesto) y filtramos por fecha en Python.
        from app.api.predictions import _start_of_today_colombia
        start_today = _start_of_today_colombia()
        old_docs = (
            db.collection("predictions")
            .where("status", "==", "active")
            .limit(500)
            .get()
        )
        batch = db.batch()
        deleted = 0
        for doc in old_docs:
            data = doc.to_dict()
            created = data.get("created_at")
            if created and hasattr(created, "replace"):
                # Firestore Timestamp -> datetime
                created_dt = created.replace(tzinfo=dt.timezone.utc) if created.tzinfo is None else created
            else:
                created_dt = None
            if created_dt and created_dt >= start_today:
                batch.delete(doc.reference)
                deleted += 1
        if deleted:
            batch.commit()
            logger.info("Borradas %d predicciones anteriores de hoy", deleted)

        # 2) Escribir las nuevas
        batch = db.batch()
        count = 0
        for pred in predictions:
            doc_ref = db.collection("predictions").document(
                f"{pred.match_id}_{pred.selection}"
            )
            data = pred.model_dump()  # datetimes -> Firestore Timestamp
            batch.set(doc_ref, data)
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
        if count % 400 != 0:
            batch.commit()
        logger.info("Publicados %d pronósticos", count)
        return count

    async def run(self, *, dry: bool = False) -> int:
        predictions = await self.collect_predictions()
        if dry or not predictions:
            return len(predictions)
        return await self.publish(predictions)