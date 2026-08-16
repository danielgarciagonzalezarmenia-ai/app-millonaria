"""Flujo de compra y gestión administrativa de premium."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from app.api import premium as premium_service
from app.api.auth import FirebaseUser, get_current_user, is_admin
from app.core.config import settings

router = APIRouter(prefix="/api/purchase", tags=["purchase"])


class PurchaseIntent(BaseModel):
    product_id: str = "premium_monthly"
    amount: float | None = None


class PurchaseIntentResponse(BaseModel):
    order_id: str
    payment_url: str
    amount: float
    currency: str = "USD"


class GrantPremiumBody(BaseModel):
    email: EmailStr
    days: int = Field(default=30, ge=1, le=3650)
    admin: bool = False


@router.post("/intent", response_model=PurchaseIntentResponse)
async def create_purchase_intent(
    body: PurchaseIntent,
    user: FirebaseUser = Depends(get_current_user),
) -> PurchaseIntentResponse:
    """Crea una orden y devuelve el link de pago de TipsterPage con la
    referencia única de la compra, para poder vincular el pago a la cuenta."""
    amount = body.amount or settings.premium_price_usd
    order = premium_service.create_order(
        user.uid, body.product_id, amount=amount
    )

    if not settings.tipsterpage_product_url:
        raise HTTPException(
            status_code=503,
            detail="El link de pago aún no está configurado en el servidor.",
        )
    sep = "&" if "?" in settings.tipsterpage_product_url else "?"
    payment_url = f"{settings.tipsterpage_product_url}{sep}ref={order['order_id']}"

    return PurchaseIntentResponse(
        order_id=order["order_id"],
        payment_url=payment_url,
        amount=amount,
    )


@router.post("/admin/grant")
async def grant_premium(
    body: GrantPremiumBody,
    request: Request,
    user: FirebaseUser = Depends(get_current_user),
) -> dict:
    """Solo admin: sube una cuenta a premium manualmente (fallback)."""
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Solo administradores.")
    return premium_service.grant_manual_premium(
        email=body.email, days=body.days, admin=body.admin
    )