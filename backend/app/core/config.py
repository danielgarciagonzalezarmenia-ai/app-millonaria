"""Configuración central protegida mediante variables de entorno.

NUNCA se hardcodean secretos. Todo se lee desde el entorno / archivo .env
que NO se sube al repositorio.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Firebase ---
    firebase_project_id: str = ""
    firebase_database_url: str = ""

    # --- Webhook de TipsterPage ---
    # Secreto usado para verificar que la petición realmente viene de
    # TipsterPage (firma HMAC-SHA256) y no de un tercero malicioso.
    tipsterpage_webhook_secret: str = ""
    # URL del producto que creaste en TipsterPage (link de pago por producto).
    tipsterpage_product_url: str = ""
    premium_price_usd: float = 9.99

    # --- Compañía ---
    app_url: str = "http://localhost:5173"
    admin_uids: list[str] = []
    env: str = "development"
    cors_origins: list[str] = ["http://localhost:5173"]

    # --- Scraper ---
    scraper_base_url: str = "https://webws.365scores.com"
    scraped_matches_limit: int = 30
    # Si se rellena, solo se analizan estas ligas (nombres exactos de 365scores).
    scraper_leagues: list[str] = []
    min_odds: float = 1.70
    premium_leagues: list[str] = []

    # --- Política gratis/día ---
    # Con pocos pronósticos al día se regala 1; con bastantes, 2.
    free_predictions_when_few: int = 1
    free_predictions_when_many: int = 2
    # Si hay menos pronósticos que este umbral se considera "pocos".
    free_predictions_threshold: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()