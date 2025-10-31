import re
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Listing, Comment, BannedPattern
from .authjwt import encode_jwt


User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id', 'username']


class ListingCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [
            'id', 'avito_url', 'title', 'image_url', 'price', 'view_count',
        ]
        read_only_fields = ['id', 'view_count']


class ListingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [
            'id', 'avito_url', 'title', 'image_url', 'price', 'description',
            'view_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']


class ListingShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'image_url', 'price', 'view_count']
        read_only_fields = ['id', 'title', 'image_url', 'price', 'view_count']


class ListingByUrlRequestSerializer(serializers.Serializer):
    url = serializers.URLField()


class CommentSerializer(serializers.ModelSerializer):
    """
    Unified serializer for read & write operations on comments.
    - Read-only: id, user, listing, likes_count, created_at, updated_at, edited, deleted
    - Writable: content
    On update, if content changes, sets edited=True.
    On representation, if deleted=True, returns placeholder in content field.
    Validates content against active BannedPattern records.
    """

    user = UserPublicSerializer(read_only=True)
    listing = serializers.PrimaryKeyRelatedField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'listing', 'user', 'content', 'likes_count',
            'edited', 'deleted', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'listing', 'user', 'likes_count', 'edited', 'deleted', 'created_at', 'updated_at',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.deleted:
            data['content'] = Comment.PLACEHOLDER_DELETED
        return data

    def validate_content(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError('Content cannot be blank.')
        text = value
        lowered = text.lower()
        violations = []
        for bp in BannedPattern.objects.active():
            if bp.is_regex:
                try:
                    if re.search(bp.pattern, text, flags=re.IGNORECASE):
                        violations.append(bp.pattern)
                except re.error:
                    if bp.pattern.lower() in lowered:
                        violations.append(bp.pattern)
            else:
                if bp.pattern.lower() in lowered:
                    violations.append(bp.pattern)
        if violations:
            raise serializers.ValidationError('Comment contains banned patterns.')
        return value

    def create(self, validated_data):
        listing = self.context.get('listing')
        if listing is None and self.context.get('listing_id') is not None:
            listing = get_object_or_404(Listing, pk=self.context['listing_id'])
        if listing is None:
            raise serializers.ValidationError({'listing': 'Listing context is required for comment creation.'})

        user = self.context.get('user')
        if user is None:
            request = self.context.get('request')
            user = getattr(request, 'user', None)
        if user is None or not getattr(user, 'is_authenticated', False):
            raise serializers.ValidationError({'user': 'Authenticated user is required for comment creation.'})

        return Comment.objects.create(listing=listing, user=user, **validated_data)

    def update(self, instance, validated_data):
        new_content = validated_data.get('content', instance.content)
        if new_content != instance.content:
            instance.content = new_content
            instance.edited = True
        instance.save(update_fields=['content', 'edited', 'updated_at'])
        return instance


class BannedPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannedPattern
        fields = ['id', 'pattern', 'is_regex', 'description', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# --- Auth serializers ---

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    password = serializers.CharField(min_length=6, max_length=128, write_only=True)

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def create(self, validated_data):
        user = User(username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"username": "Invalid credentials."})
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Invalid credentials."})

        token = encode_jwt({"user_id": user.id})
        attrs["token"] = token
        self.user = user  # attach for view usage
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "date_joined"]
        read_only_fields = ["id", "username", "date_joined"]


class AuthResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    token = serializers.CharField()


# ===== Comments feature serializers =====

class CommentReadSerializer(serializers.ModelSerializer):
    """Read serializer for comments with masked content if deleted and ownership flag."""

    PLACEHOLDER_TEXT = "Комментарий удалён пользователем"

    user = UserPublicSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'user', 'created_at', 'updated_at', 'edited', 'deleted', 'likes_count', 'is_owner',
        ]
        read_only_fields = fields

    def get_is_owner(self, obj: Comment) -> bool:
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not getattr(user, 'is_authenticated', False):
            return False
        return obj.user_id == user.id

    def get_content(self, obj: Comment) -> str:
        if obj.deleted:
            return self.PLACEHOLDER_TEXT
        return obj.content


class CommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1, allow_blank=False, trim_whitespace=True)


class CommentUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=False, trim_whitespace=True)


class BannedViolationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    description = serializers.CharField(allow_blank=True)


class CommentLikeToggleSerializer(serializers.Serializer):
    liked = serializers.BooleanField()
    likes_count = serializers.IntegerField()


# ===== Utility and response serializers =====

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)
    timestamp = serializers.DateTimeField()


class CommentsListResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    results = CommentReadSerializer(many=True, read_only=True)
