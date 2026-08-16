"""Generación y verificación de firmas HMAC para webhooks.

Cualquier notificación de pago que reciba el backend debe venir firmada por
TipsterPage con la cabecera `X-TipsterPage-Signature` (HMAC-SHA256 del body).
Sin una firma válida la petición se rechaza.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


def sign_payload(payload: bytes | str, secret: str) -> str:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    return hmac.new(
        secret.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()


def verify_signature(payload: bytes | str, signature: str, secret: str) -> bool:
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(expected, signature.strip().lower())


def canonical_json(data: Any) -> bytes:
    """Serializa el body de forma determinista para poder firmarlo/verificarlo."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")