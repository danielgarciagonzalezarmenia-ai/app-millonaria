"""EJECUTA EL PIPELINE DE SCRAPING -> PUBLICAR PRONÓSTICOS.

Uso:
  python run_scraper.py            # procesa y publica en Firestore
  python run_scraper.py --dry      # solo inspecciona, no publica
  python run_scraper.py --games 20 # limita a 20 partidos

Configura primero el .env (copiar backend/.env.example).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

from app.scraper.pipeline import PredictionPipeline  # noqa: E402


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="no publicar en Firestore")
    parser.add_argument("--games", type=int, default=None, help="limitar nº de partidos")
    args = parser.parse_args()

    pipeline = PredictionPipeline(max_games=args.games)

    if args.dry:
        predictions = await pipeline.collect_predictions()
        for p in predictions:
            flag = "PREMIUM" if p.premium else "free"
            print(
                f"[{flag}] {p.league:<22} {p.home_team} vs {p.away_team} "
                f"-> {p.market:<26} @ {p.odds:.2f}  ({p.confidence:.0%})"
            )
        print(f"\n{len(predictions)} predicciones generadas.")
        return

    count = await pipeline.run()
    print(f"\nPublicadas {count} predicciones en Firestore.")


if __name__ == "__main__":
    asyncio.run(main())