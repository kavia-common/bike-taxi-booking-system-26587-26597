from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional

from src.api.schemas import PaymentInit, PaymentOut
from src.api.models import PAYMENTS, Payment, PaymentStatus, RIDES, RideStatus, Role
from src.api.models import gen_id
from src.api.auth import require_role
from src.api.config import settings

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/init", summary="Initiate payment", response_model=PaymentOut)
def initiate_payment(body: PaymentInit, user=Depends(require_role(Role.PASSENGER))):
    """Initiate a payment for a completed ride; returns a pseudo provider ref."""
    ride = RIDES.get(body.ride_id)
    if not ride or ride.passenger_id != user.id:
        raise HTTPException(status_code=404, detail="Ride not found")
    if ride.status != RideStatus.COMPLETED or ride.fare_final is None:
        raise HTTPException(status_code=400, detail="Ride not completed")
    pay = Payment(
        id=gen_id(),
        ride_id=ride.id,
        amount=float(ride.fare_final),
        currency="USD",
        status=PaymentStatus.AUTHORIZED,  # as if provider authorized immediately for demo
        provider_ref="prov_" + gen_id(),
    )
    PAYMENTS[pay.id] = pay
    return PaymentOut(**{**pay.__dict__, "status": pay.status.value})


@router.post("/webhook", summary="Payment provider webhook")
def payment_webhook(x_signature: Optional[str] = Header(default=None), ref: Optional[str] = None, status: Optional[str] = None):
    """Webhook endpoint to process payment provider callbacks.

    Headers:
        X-Signature: HMAC or token signature (demo verification).
    Query:
        ref: provider_ref identifier
        status: new status (captured, failed, refunded)
    """
    secret = settings.payment_provider_secret or "dev-pay-secret"
    # very simple token check for demo
    if x_signature != secret:
        raise HTTPException(status_code=401, detail="Invalid signature")
    # find payment by provider_ref
    payment = next((p for p in PAYMENTS.values() if p.provider_ref == ref), None)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    map_status = {
        "captured": PaymentStatus.CAPTURED,
        "failed": PaymentStatus.FAILED,
        "refunded": PaymentStatus.REFUNDED,
    }
    if status not in map_status:
        raise HTTPException(status_code=400, detail="Invalid status")
    payment.status = map_status[status]
    return {"ok": True, "payment_id": payment.id, "status": payment.status.value}
