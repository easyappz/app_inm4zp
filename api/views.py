from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authjwt import encode_jwt
from .serializers import (
    MessageSerializer,  # assuming existing
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    AuthResponseSerializer,
)


class HelloView(APIView):
    """
    A simple API endpoint that returns a greeting message.
    """

    @extend_schema(
        responses={200: MessageSerializer}, description="Get a hello world message"
    )
    def get(self, request):
        data = {"message": "Hello!", "timestamp": timezone.now()}
        serializer = MessageSerializer(data)
        return Response(serializer.data)


class AuthRegisterView(APIView):
    """Register a new user and return a JWT token."""

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: AuthResponseSerializer,
            400: {"description": "Validation error"},
        },
        description="Register a new user and receive a JWT token.",
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        token = encode_jwt({"user_id": user.id})
        data = {"user": UserSerializer(user).data, "token": token}
        return Response(data, status=status.HTTP_201_CREATED)


class AuthLoginView(APIView):
    """Login with username and password and return a JWT token."""

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: AuthResponseSerializer,
            400: {"description": "Invalid credentials"},
        },
        description="Login and receive a JWT token.",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = getattr(serializer, "user", None)
        token = serializer.validated_data["token"]
        data = {"user": UserSerializer(user).data, "token": token}
        return Response(data, status=status.HTTP_200_OK)


class AuthMeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: UserSerializer,
            401: {"description": "Unauthorized"},
        },
        description="Get current authenticated user.",
    )
    def get(self, request):
        return Response(UserSerializer(request.user).data)
