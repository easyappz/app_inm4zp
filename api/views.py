from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.db.models import F
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import re

from .authjwt import encode_jwt
from .models import Listing, Comment, BannedPattern, CommentLike
from .serializers import (
    MessageSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    AuthResponseSerializer,
    ListingShortSerializer,
    ListingDetailSerializer,
    ListingByUrlRequestSerializer,
    CommentReadSerializer,
    CommentCreateSerializer,
    CommentUpdateSerializer,
    BannedViolationSerializer,
    CommentLikeToggleSerializer,
    CommentsListResponseSerializer,
)
from .services.avito import fetch_avito_data


class HelloView(APIView):
    """
    A simple API endpoint that returns a greeting message.
    """

    @extend_schema(
        responses={200: MessageSerializer},
        description="Get a hello world message",
        tags=["misc"],
        examples=[
            OpenApiExample(
                "HelloResponse",
                value={"message": "Hello!", "timestamp": "2025-01-01T12:00:00Z"},
                response_only=True,
                status_codes=["200"],
            )
        ],
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
        tags=["auth"],
        examples=[
            OpenApiExample(
                "RegisterRequest",
                value={"username": "alice", "password": "secret123"},
                request_only=True,
                status_codes=["201", "400"],
            ),
            OpenApiExample(
                "RegisterResponse",
                value={
                    "user": {"id": 1, "username": "alice", "date_joined": "2025-01-01T00:00:00Z"},
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
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
        tags=["auth"],
        examples=[
            OpenApiExample(
                "LoginRequest",
                value={"username": "alice", "password": "secret123"},
                request_only=True,
                status_codes=["200", "400"],
            ),
            OpenApiExample(
                "LoginResponse",
                value={
                    "user": {"id": 1, "username": "alice", "date_joined": "2025-01-01T00:00:00Z"},
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
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
        tags=["auth"],
        examples=[
            OpenApiExample(
                "AuthMeResponse",
                value={"id": 1, "username": "alice", "date_joined": "2025-01-01T00:00:00Z"},
                response_only=True,
                status_codes=["200"],
            )
        ],
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
        examples=[
            OpenApiExample(
                "PopularListingsResponse",
                value=[
                    {"id": 10, "title": "iPhone 13 Pro", "image_url": "https://example.com/img1.jpg", "price": "79999.00", "view_count": 1280},
                    {"id": 11, "title": "PlayStation 5", "image_url": "https://example.com/img2.jpg", "price": "55999.00", "view_count": 990},
                ],
                response_only=True,
                status_codes=["200"],
            )
        ],
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
        examples=[
            OpenApiExample(
                "ListingByUrlRequest",
                value={"url": "https://www.avito.ru/item/123456"},
                request_only=True,
                status_codes=["200", "201", "400", "422"],
            ),
            OpenApiExample(
                "ListingByUrlResponseCreated",
                value={
                    "id": 20,
                    "avito_url": "https://www.avito.ru/item/123456",
                    "title": "MacBook Air 13",
                    "image_url": "https://example.com/mac.jpg",
                    "price": "89999.00",
                    "description": "Excellent condition",
                    "view_count": 0,
                    "created_at": "2025-01-02T10:00:00Z",
                    "updated_at": "2025-01-02T10:00:00Z",
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
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
                return Response({"url": ["Invalid URL"]}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
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
        examples=[
            OpenApiExample(
                "ListingDetailResponse",
                value={
                    "id": 20,
                    "avito_url": "https://www.avito.ru/item/123456",
                    "title": "MacBook Air 13",
                    "image_url": "https://example.com/mac.jpg",
                    "price": "89999.00",
                    "description": "Excellent condition",
                    "view_count": 101,
                    "created_at": "2025-01-02T10:00:00Z",
                    "updated_at": "2025-01-03T14:00:00Z",
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, request, pk: int):
        listing = get_object_or_404(Listing, pk=pk)
        Listing.objects.filter(pk=listing.pk).update(view_count=F("view_count") + 1)
        listing.refresh_from_db(fields=["view_count", "updated_at"])  # ensure actual value
        return Response(ListingDetailSerializer(listing).data)


# ===== Comments feature =====

def _find_banned_violations(text: str):
    """Return list of {id, description} for active BannedPattern that match text."""
    if not text:
        return []
    text = str(text)
    lowered = text.lower()
    violations = []
    for bp in BannedPattern.objects.active():
        try:
            matched = False
            if bp.is_regex:
                matched = re.search(bp.pattern, text, flags=re.IGNORECASE) is not None
            else:
                matched = bp.pattern.lower() in lowered
            if matched:
                violations.append({"id": bp.id, "description": bp.description or ""})
        except re.error:
            if bp.pattern.lower() in lowered:
                violations.append({"id": bp.id, "description": bp.description or ""})
    return violations


class CommentListCreateView(APIView):
    """List and create comments for a listing."""

    @extend_schema(
        parameters=[
            OpenApiParameter(name='limit', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Limit (default 20, max 100)', required=False),
            OpenApiParameter(name='offset', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, description='Offset (default 0)', required=False),
        ],
        responses={
            200: CommentsListResponseSerializer,
            404: {"description": "Listing not found"},
        },
        description="List comments for listing ordered by created_at desc with limit/offset pagination.",
        tags=["comments"],
        examples=[
            OpenApiExample(
                "CommentsListResponse",
                value={
                    "count": 1,
                    "limit": 20,
                    "offset": 0,
                    "results": [
                        {
                            "id": 100,
                            "content": "Great item!",
                            "user": {"id": 1, "username": "alice"},
                            "created_at": "2025-01-03T12:00:00Z",
                            "updated_at": "2025-01-03T12:00:00Z",
                            "edited": False,
                            "deleted": False,
                            "likes_count": 3,
                            "is_owner": False,
                        }
                    ],
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, request, listing_id: int):
        listing = get_object_or_404(Listing, pk=listing_id)
        try:
            limit = int(request.query_params.get('limit', 20))
        except (TypeError, ValueError):
            limit = 20
        try:
            offset = int(request.query_params.get('offset', 0))
        except (TypeError, ValueError):
            offset = 0
        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        qs = Comment.objects.filter(listing_id=listing.id).order_by('-created_at')
        count = qs.count()
        items = qs[offset: offset + limit]
        data = CommentReadSerializer(items, many=True, context={'request': request}).data
        return Response({
            'count': count,
            'limit': limit,
            'offset': offset,
            'results': data,
        })

    @extend_schema(
        request=CommentCreateSerializer,
        responses={
            201: CommentReadSerializer,
            400: BannedViolationSerializer(many=True),
            401: {"description": "Unauthorized"},
            404: {"description": "Listing not found"},
        },
        description="Create a comment for listing. Validates content against active BannedPattern.",
        tags=["comments"],
        examples=[
            OpenApiExample(
                "CreateCommentRequest",
                value={"content": "Great item!"},
                request_only=True,
                status_codes=["201", "400"],
            ),
            OpenApiExample(
                "CreateCommentResponse",
                value={
                    "id": 101,
                    "content": "Great item!",
                    "user": {"id": 1, "username": "alice"},
                    "created_at": "2025-01-03T12:10:00Z",
                    "updated_at": "2025-01-03T12:10:00Z",
                    "edited": False,
                    "deleted": False,
                    "likes_count": 0,
                    "is_owner": True,
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "CreateCommentViolation",
                value=[{"id": 1, "description": "No phone numbers"}],
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request, listing_id: int):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        listing = get_object_or_404(Listing, pk=listing_id)
        serializer = CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        content = serializer.validated_data['content']
        violations = _find_banned_violations(content)
        if violations:
            return Response(violations, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(listing=listing, user=request.user, content=content)
        return Response(CommentReadSerializer(comment, context={'request': request}).data, status=status.HTTP_201_CREATED)


class CommentDetailView(APIView):
    """Retrieve, update (owner only), delete (soft delete) a comment."""

    @extend_schema(
        responses={
            200: CommentReadSerializer,
            404: {"description": "Not found"},
        },
        description="Retrieve a single comment by ID.",
        tags=["comments"],
        examples=[
            OpenApiExample(
                "CommentDetailResponse",
                value={
                    "id": 100,
                    "content": "Great item!",
                    "user": {"id": 2, "username": "bob"},
                    "created_at": "2025-01-03T12:00:00Z",
                    "updated_at": "2025-01-03T12:00:00Z",
                    "edited": False,
                    "deleted": False,
                    "likes_count": 3,
                    "is_owner": False,
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def get(self, request, pk: int):
        comment = get_object_or_404(Comment, pk=pk)
        return Response(CommentReadSerializer(comment, context={'request': request}).data)

    @extend_schema(
        request=CommentUpdateSerializer,
        responses={
            200: CommentReadSerializer,
            400: BannedViolationSerializer(many=True),
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
            404: {"description": "Not found"},
        },
        description="Update own comment (partial). Sets edited=true when content changes and re-validates against BannedPattern.",
        tags=["comments"],
        examples=[
            OpenApiExample(
                "UpdateCommentRequest",
                value={"content": "Updated content"},
                request_only=True,
                status_codes=["200", "400"],
            ),
            OpenApiExample(
                "UpdateCommentResponse",
                value={
                    "id": 100,
                    "content": "Updated content",
                    "user": {"id": 1, "username": "alice"},
                    "created_at": "2025-01-03T12:00:00Z",
                    "updated_at": "2025-01-03T12:20:00Z",
                    "edited": True,
                    "deleted": False,
                    "likes_count": 3,
                    "is_owner": True,
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "UpdateCommentViolation",
                value=[{"id": 1, "description": "No phone numbers"}],
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def patch(self, request, pk: int):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        comment = get_object_or_404(Comment, pk=pk)
        if comment.user_id != request.user.id:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        serializer = CommentUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        content = serializer.validated_data.get('content')
        if content is not None:
            violations = _find_banned_violations(content)
            if violations:
                return Response(violations, status=status.HTTP_400_BAD_REQUEST)
            if content != comment.content:
                comment.content = content
                comment.edited = True
        comment.save(update_fields=['content', 'edited', 'updated_at'])
        return Response(CommentReadSerializer(comment, context={'request': request}).data)

    @extend_schema(
        responses={
            204: {"description": "Deleted"},
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
            404: {"description": "Not found"},
        },
        description="Soft-delete own comment (mark deleted=true). The original content won't be exposed afterwards.",
        tags=["comments"],
    )
    def delete(self, request, pk: int):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        comment = get_object_or_404(Comment, pk=pk)
        if comment.user_id != request.user.id:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        if not comment.deleted:
            comment.deleted = True
            comment.save(update_fields=['deleted', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentLikeToggleView(APIView):
    """Toggle like on a comment. Authenticated users only."""

    @extend_schema(
        responses={
            200: CommentLikeToggleSerializer,
            401: {"description": "Unauthorized"},
            404: {"description": "Not found"},
        },
        description="Toggle like for a comment. If like existed, it will be removed; otherwise created.",
        tags=["comments"],
        examples=[
            OpenApiExample(
                "LikeToggleResponse",
                value={"liked": True, "likes_count": 4},
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def post(self, request, pk: int):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        comment = get_object_or_404(Comment, pk=pk)
        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        if created:
            liked = True
        else:
            like.delete()
            liked = False
        comment.refresh_from_db(fields=['likes_count'])
        return Response({"liked": liked, "likes_count": comment.likes_count})
