"""Paquete de scraping de 360score."""

from app.scraper.client import ScraperClient
from app.scraper.pipeline import PredictionPipeline

__all__ = ["ScraperClient", "PredictionPipeline"]