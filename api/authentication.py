from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .authjwt import decode_jwt


User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request) -> Optional[Tuple[User, None]]:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != self.keyword.lower():
            return None

        token = parts[1]
        payload = decode_jwt(token)

        user_id = payload.get("user_id")
        if not user_id:
            raise AuthenticationFailed("Invalid token payload.")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found.")

        return (user, None)
