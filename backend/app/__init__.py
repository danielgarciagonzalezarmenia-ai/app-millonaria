"""Aplicación FastAPI - App Millonaria."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)

__all__ = ["limiter", "settings", "CORSMiddleware"]