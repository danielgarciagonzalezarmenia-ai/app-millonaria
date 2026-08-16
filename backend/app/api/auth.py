"""Autenticación de usuarios mediante tokens de Firebase Auth.

El frontend inicia sesión con Google (Firebase Auth) y obtiene un ID token.
El backend valida ese token (firma, emisor, audiencia, expiración) y conoce
el UID del usuario. Nunca se confía en el UID que mande el cliente.
"""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from firebase_admin import auth as firebase_auth

from app.core import firebase


class AuthError(HTTPException):
    pass


def _verify_id_token(id_token: str) -> dict:
    try:
        return firebase_auth.verify_id_token(id_token, app=firebase.get_app())
    except Exception as exc:  # token inválido, expirado o malformado
        raise AuthError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada.",
        ) from exc


class FirebaseUser:
    """Info del usuario autenticado."""

    def __init__(self, uid: str, email: str | None, claims: dict) -> None:
        self.uid = uid
        self.email = email
        self.claims = claims

    @property
    def is_premium(self) -> bool:
        return bool(self.claims.get("premium", False))


def get_current_user(
    authorization: str | None = Header(default=None),
) -> FirebaseUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autorización.",
        )
    id_token = authorization.split(" ", 1)[1].strip()
    decoded = _verify_id_token(id_token)
    return FirebaseUser(
        uid=decoded.get("uid", ""),
        email=decoded.get("email"),
        claims=decoded.get("claims", {}),
    )


def get_optional_user(
    authorization: str | None = Header(default=None),
) -> FirebaseUser | None:
    """Igual que get_current_user pero devuelve None si no hay sesión.

    Permite endpoints públicos que mejoran su respuesta cuando hay sesión
    (ej: un anónimo ve los gratis, un premium ve todos).
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    id_token = authorization.split(" ", 1)[1].strip()
    decoded = _verify_id_token(id_token)
    return FirebaseUser(
        uid=decoded.get("uid", ""),
        email=decoded.get("email"),
        claims=decoded.get("claims", {}),
    )


def require_premium(user: FirebaseUser = Depends(get_current_user)) -> FirebaseUser:
    if not user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Suscripción premium requerida.",
        )
    return user


def is_admin(user: FirebaseUser) -> bool:
    return bool(user.claims.get("admin", False)) or user.uid in _admins()


def _admins() -> set[str]:
    from app.core.config import settings

    return set(settings.admin_uids)