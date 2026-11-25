import hmac
import hashlib
import json
import requests
from django.utils import timezone

def generate_hmac_signature(secret_key, payload_bytes):
    """
    Generates HMAC SHA-256 signature for webhook payload.
    """
    if isinstance(secret_key, str):
        secret_key = secret_key.encode('utf-8')
    return hmac.new(secret_key, payload_bytes, hashlib.sha256).hexdigest()

def dispatch_payment_webhook(payment_order, event_type="payment.success"):
    """
    Dispatches webhook notification for a PaymentOrder to all active WebhookEndpoints of the merchant.
    """
    from cloth_app.models import WebhookEndpoint, WebhookDelivery

    merchant = payment_order.merchant
    endpoints = WebhookEndpoint.objects.filter(merchant=merchant, is_active=True)

    payload = {
        "event": event_type,
        "mode": payment_order.mode,
        "payment_id": payment_order.payment_id,
        "order_id": payment_order.order_id,
        "amount": float(payment_order.amount),
        "currency": payment_order.currency,
        "status": payment_order.status,
        "provider_reference": payment_order.provider_reference or "",
        "created_at": payment_order.created_at.isoformat() if payment_order.created_at else "",
        "timestamp": timezone.now().isoformat()
    }

    payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')

    deliveries = []
    for ep in endpoints:
        signature = generate_hmac_signature(ep.secret_key, payload_bytes)
        headers = {
            "Content-Type": "application/json",
            "X-Gateway-Signature": signature,
            "X-Gateway-Event": event_type,
            "User-Agent": "US-VESTA-Gateway-Webhook/1.0"
        }

        delivered = False
        response_status = None
        try:
            resp = requests.post(ep.target_url, data=payload_bytes, headers=headers, timeout=5)
            response_status = resp.status_code
            if 200 <= resp.status_code < 300:
                delivered = True
        except Exception:
            response_status = 500

        delivery = WebhookDelivery.objects.create(
            webhook_endpoint=ep,
            payment_order=payment_order,
            event_type=event_type,
            request_payload=payload,
            response_status=response_status,
            delivered=delivered,
            delivered_at=timezone.now() if delivered else None,
            attempts=1
        )
        deliveries.append(delivery)

    return deliveries
