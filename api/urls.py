from django.urls import path
from .views import (
    HelloView,
    AuthRegisterView,
    AuthLoginView,
    AuthMeView,
    PopularListingsView,
    ListingByUrlView,
    ListingDetailView,
    CommentListCreateView,
    CommentDetailView,
    CommentLikeToggleView,
)

urlpatterns = [
    path("hello/", HelloView.as_view(), name="hello"),
    path("auth/register/", AuthRegisterView.as_view(), name="auth-register"),
    path("auth/login/", AuthLoginView.as_view(), name="auth-login"),
    path("auth/me/", AuthMeView.as_view(), name="auth-me"),

    # Listings
    path("listings/popular/", PopularListingsView.as_view(), name="listings-popular"),
    path("listings/by-url/", ListingByUrlView.as_view(), name="listings-by-url"),
    path("listings/<int:pk>/", ListingDetailView.as_view(), name="listing-detail"),

    # Comments
    path("listings/<int:listing_id>/comments/", CommentListCreateView.as_view(), name="listing-comments"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("comments/<int:pk>/like/", CommentLikeToggleView.as_view(), name="comment-like-toggle"),
]
