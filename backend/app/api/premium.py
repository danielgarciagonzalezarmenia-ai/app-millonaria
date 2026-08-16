"""Servicio de gestión de cuentas premium.

Al detectar el pago, marcamos al usuario como premium:
1. Escribimos el estado en Firestore (collection `users/{uid}`).
2. Aplicamos custom claims en Firebase Auth para que `require_premium` funcione
   en el backend y que las reglas de Firestore puedan leer `request.auth.token.premium`.

El método idempotente: si el mismo payment_id llega dos veces, no se duplica.
"""

from __future__ import annotations

import datetime as dt
import logging
import secrets
import uuid

from firebase_admin import auth as firebase_auth

from app.core import firebase

logger = logging.getLogger("premium")

PREMIUM_DAYS = 30  # duración de un pago premium


class PremiumError(Exception):
    pass


# ---------- Ordenes de compra ----------

def create_order(uid: str, product_id: str, *, amount: float, currency: str = "USD") -> dict:
    """Crea una orden pendiente vinculada a la cuenta del usuario."""
    order_id = f"{uid[:8]}-{uuid.uuid4().hex[:12]}"
    order = {
        "order_id": order_id,
        "uid": uid,
        "product_id": product_id,
        "amount": amount,
        "currency": currency,
        "status": "pending",
        "created_at": dt.datetime.now(datetime.UTC).isoformat(),
        "payment_id": None,
        "paid_at": None,
    }
    db = firebase.db()
    db.collection("orders").document(order_id).set(order)
    return order


def get_order(order_id: str) -> dict | None:
    snapshot = firebase.db().collection("orders").document(order_id).get()
    return snapshot.to_dict() if snapshot.exists else None


def _find_order_by_payment(payment_id: str) -> dict | None:
    rows = (
        firebase.db()
        .collection("orders")
        .where("payment_id", "==", payment_id)
        .limit(1)
        .get()
    )
    for row in rows:
        return row.to_dict()
    return None


# ---------- Activación de premium ----------

def activate_premium_for_order(order_id: str, payment_id: str, buyer_email: str | None) -> dict:
    db = firebase.db()
    order = _find_order_by_payment(payment_id) or get_order(order_id)
    if order is None:
        # Intentamos vincular por email si no tenemos la order.
        if buyer_email:
            row = _find_user_by_email(buyer_email)
            if row is None:
                raise PremiumError(
                    f"No existe cuenta para afiliar premium ({buyer_email}). "
                    "El usuario debe registrarse con Google antes de pagar."
                )
            order = _build_order_from_user(row, payment_id)
        else:
            raise PremiumError("Pago sin orden ni email para vincular.")

    if order.get("status") == "paid":
        return order  # idempotente

    uid = order["uid"]
    expires_at = dt.datetime.now(datetime.UTC) + dt.timedelta(days=PREMIUM_DAYS)

    # Custom claims en Auth (afecta al toki'n del usuario).
    app = firebase.get_app()
    claims = (firebase_auth.get_user(uid, app=app).custom_claims or {}).copy()
    claims["premium"] = True
    claims["premium_until"] = expires_at.isoformat()
    firebase_auth.set_custom_user_claims(uid, claims, app=app)

    # Estado en Firestore.
    now = dt.datetime.now(datetime.UTC).isoformat()
    db.collection("users").document(uid).set(
        {
            "premium": True,
            "premium_since": now,
            "premium_until": expires_at.isoformat(),
        },
        merge=True,
    )
    order.update(
        {
            "status": "paid",
            "payment_id": payment_id,
            "paid_at": now,
            "premium_until": expires_at.isoformat(),
            "buyer_email": buyer_email,
        }
    )
    db.collection("orders").document(order["order_id"]).set(order, merge=True)
    logger.info("Premium activado para uid=%s (order=%s)", uid, order["order_id"])
    return order


def _find_user_by_email(email: str) -> dict | None:
    app = firebase.get_app()
    try:
        user = firebase_auth.get_user_by_email(email, app=app)
    except firebase_auth.UserNotFoundError:
        return None
    return {"uid": user.uid, "email": email}


def _build_order_from_user(user: dict, payment_id: str) -> dict:
    order = {
        "order_id": f"{user['uid'][:8]}-{uuid.uuid4().hex[:12]}",
        "uid": user["uid"],
        "product_id": "premium_paid",  # garantia: order creada por webhook
        "amount": 0.0,
        "currency": "USD",
        "status": "pending",
        "created_at": dt.datetime.now(datetime.UTC).isoformat(),
        "payment_id": payment_id,
        "paid_at": None,
        "buyer_email": user["email"],
    }
    firebase.db().collection("orders").document(order["order_id"]).set(order)
    return order


# ---------- Admin manual ----------

def grant_manual_premium(email: str, *, days: int = PREMIUM_DAYS, admin: bool = False) -> dict:
    """OTP: sube premium manualmente (usado cuando el webhook no llega o fallback)."""
    app = firebase.get_app()
    user = firebase_auth.get_user_by_email(email, app=app)
    expires_at = dt.datetime.now(datetime.UTC) + dt.timedelta(days=days)
    claims = (user.custom_claims or {}).copy()
    claims["premium"] = True
    claims["premium_until"] = expires_at.isoformat()
    if admin:
        claims["admin"] = True
    firebase_auth.set_custom_user_claims(user.uid, claims, app=app)
    now = dt.datetime.now(datetime.UTC).isoformat()
    firebase.db().collection("users").document(user.uid).set(
        {
            "premium": True,
            "premium_since": now,
            "premium_until": expires_at.isoformat(),
            "admin": admin,
        },
        merge=True,
    )
    return {"uid": user.uid, "premium_until": expires_at.isoformat(), "admin": admin}