"""Aplicación FastAPI de App Millonaria.

Monta routers, limpieza de CORS, rate limiting global y cabeceras de seguridad.
"""

from __future__ import annotations

import time

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import auth as firebase_auth
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import JSONResponse

from app.api import predictions, purchase, webhooks, admin
from app.api.auth import FirebaseUser, get_current_user
from app.core import firebase
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="App Millonaria API",
    version="0.1.0",
    docs_url="/docs" if settings.env != "production" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.env != "production" else None,
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS: solo orígenes permitidos (el dominio de la web).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in settings.cors_origins if origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-TipsterPage-Signature", "X-Hub-Signature"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["X-Powered-By"] = "App Millonaria"
    response.headers["X-Response-Time"] = f"{time.monotonic() - start:.3f}s"
    return response


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Demasiadas peticiones."})


app.include_router(predictions.router)
app.include_router(purchase.router)
app.include_router(webhooks.router)
app.include_router(admin.router)


@app.get("/")
async def root() -> dict:
    return {"app": "App Millonaria", "status": "ok"}


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/me")
async def me(user: FirebaseUser = Depends(get_current_user)) -> dict:
    return {
        "uid": user.uid,
        "email": user.email,
        "premium": user.is_premium,
        "premium_until": user.claims.get("premium_until"),
    }


@app.post("/api/refresh-claims")
async def refresh_claims(user: FirebaseUser = Depends(get_current_user)) -> dict:
    """Devuelve los claims frescos (los custom claims tardan en propagarse)."""
    refreshed = firebase_auth.get_user(user.uid, app=firebase.get_app())
    fresh_claims = refreshed.custom_claims or {}
    from app.api.auth import is_admin
    fresh_user = FirebaseUser(uid=user.uid, email=user.email, claims=fresh_claims)
    return {
        "premium": bool(fresh_claims.get("premium")),
        "premium_until": fresh_claims.get("premium_until"),
        "admin": is_admin(fresh_user),
    }