import hashlib
from cloth_app.models import APIKey, Merchant

def authenticate_api_keys(request):
    """
    Parses X-Api-Public-Key and X-Api-Secret-Key headers.
    Validates active key pair and merchant status.
    Returns (merchant, api_key_obj) or (None, None).
    """
    pub_key = request.headers.get("X-Api-Public-Key") or request.META.get("HTTP_X_API_PUBLIC_KEY")
    sec_key = request.headers.get("X-Api-Secret-Key") or request.META.get("HTTP_X_API_SECRET_KEY")

    if not pub_key or not sec_key:
        return None, None

    try:
        api_key_obj = APIKey.objects.select_related('merchant').get(
            public_key=pub_key,
            is_active=True
        )
    except APIKey.DoesNotExist:
        return None, None

    if api_key_obj.merchant.status != 'ACTIVE':
        return None, None

    incoming_hash = hashlib.sha256(sec_key.encode('utf-8')).hexdigest()
    if incoming_hash != api_key_obj.secret_key_hash:
        return None, None

    return api_key_obj.merchant, api_key_obj
