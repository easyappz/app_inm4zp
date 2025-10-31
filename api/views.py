from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authjwt import encode_jwt
from .models import Listing
from .serializers import (
    MessageSerializer,  # assuming existing
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    AuthResponseSerializer,
    ListingShortSerializer,
    ListingDetailSerializer,
    ListingByUrlRequestSerializer,
)
from .services.avito import fetch_avito_data


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


class PopularListingsView(APIView):
    """Return most viewed listings."""

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Max items to return (default 20, max 100)",
            )
        ],
        responses={200: ListingShortSerializer(many=True)},
        description="Get top listings by view_count.",
        tags=["listings"],
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 20))
        except (TypeError, ValueError):
            limit = 20
        limit = max(1, min(limit, 100))
        qs = Listing.objects.popular()[:limit]
        return Response(ListingShortSerializer(qs, many=True).data)


class ListingByUrlView(APIView):
    """Get or create listing by Avito URL."""

    @extend_schema(
        request=ListingByUrlRequestSerializer,
        responses={
            200: ListingDetailSerializer,
            201: ListingDetailSerializer,
            400: {"description": "Invalid URL"},
            422: {"description": "Unable to fetch or parse listing"},
        },
        description="If listing with given URL exists, return it. Otherwise fetch data from URL, create a new listing and return it.",
        tags=["listings"],
    )
    def post(self, request):
        req = ListingByUrlRequestSerializer(data=request.data)
        if not req.is_valid():
            return Response(req.errors, status=status.HTTP_400_BAD_REQUEST)

        url = req.validated_data["url"].strip()

        try:
            existing = Listing.objects.filter(avito_url=url).first()
            if existing:
                return Response(ListingDetailSerializer(existing).data, status=status.HTTP_200_OK)

            try:
                data = fetch_avito_data(url)
            except ValueError:
                # invalid URL format case (should be caught by serializer but keep safe)
                return Response({"url": ["Invalid URL"]}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                # Network or other issues
                return Response({"detail": "Failed to fetch listing data."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            title = (data.get("title") or "").strip()
            if not title:
                return Response({"detail": "Unable to parse listing title."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            image_url = data.get("image_url")
            price = data.get("price")
            description = data.get("description") or ""

            try:
                obj = Listing.objects.create(
                    avito_url=url,
                    title=title[:512],
                    image_url=image_url,
                    price=price,
                    description=description,
                )
                return Response(ListingDetailSerializer(obj).data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                # Race condition: listing created in parallel
                obj = Listing.objects.get(avito_url=url)
                return Response(ListingDetailSerializer(obj).data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Unexpected error."}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class ListingDetailView(APIView):
    """Return detailed listing and increment its view_count atomically."""

    @extend_schema(
        responses={
            200: ListingDetailSerializer,
            404: {"description": "Not found"},
        },
        description="Retrieve listing by ID and increment view count.",
        tags=["listings"],
    )
    def get(self, request, pk: int):
        listing = get_object_or_404(Listing, pk=pk)
        Listing.objects.filter(pk=listing.pk).update(view_count=F("view_count") + 1)
        listing.refresh_from_db(fields=["view_count", "updated_at"])  # ensure actual value
        return Response(ListingDetailSerializer(listing).data)
