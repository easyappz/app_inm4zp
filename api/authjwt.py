import base64
import hmac
import hashlib
import json
import time
from typing import Dict, Any

from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def encode_jwt(payload: Dict[str, Any], exp_seconds: int = 7 * 24 * 3600) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    to_encode = dict(payload)
    to_encode["exp"] = now + int(exp_seconds)

    header_json = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_json = json.dumps(to_encode, separators=(",", ":"), sort_keys=True).encode("utf-8")

    header_b64 = _b64url_encode(header_json)
    payload_b64 = _b64url_encode(payload_json)

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    key = settings.SECRET_KEY.encode("utf-8")
    signature = hmac.new(key, signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_jwt(token: str) -> Dict[str, Any]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise AuthenticationFailed("Invalid token format.")
        header_b64, payload_b64, signature_b64 = parts

        header_bytes = _b64url_decode(header_b64)
        payload_bytes = _b64url_decode(payload_b64)
        signature_bytes = _b64url_decode(signature_b64)

        header = json.loads(header_bytes.decode("utf-8"))
        if header.get("alg") != "HS256":
            raise AuthenticationFailed("Unsupported token algorithm.")

        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        key = settings.SECRET_KEY.encode("utf-8")
        expected_sig = hmac.new(key, signing_input, hashlib.sha256).digest()

        if not hmac.compare_digest(signature_bytes, expected_sig):
            raise AuthenticationFailed("Invalid token signature.")

        payload = json.loads(payload_bytes.decode("utf-8"))
        exp = payload.get("exp")
        if exp is None:
            raise AuthenticationFailed("Token has no expiration.")
        if int(time.time()) >= int(exp):
            raise AuthenticationFailed("Token has expired.")

        return payload
    except AuthenticationFailed:
        raise
    except Exception:
        raise AuthenticationFailed("Invalid token.")
