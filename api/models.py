from __future__ import annotations

import re
from django.conf import settings
from django.db import models
from django.db.models import F, Index


# QuerySets for convenient filtering/ordering
class ListingQuerySet(models.QuerySet):
    def popular(self):
        return self.order_by('-view_count', '-created_at')


class CommentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)


class BannedPatternQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)


class Listing(models.Model):
    """
    Avito listing entity.
    """

    avito_url = models.URLField(unique=True, db_index=True)
    title = models.CharField(max_length=512)
    image_url = models.URLField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    view_count = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ListingQuerySet.as_manager()

    class Meta:
        ordering = ['-view_count', '-created_at']
        indexes = [
            Index(fields=['view_count']),
        ]

    def __str__(self) -> str:
        return f"Listing(id={self.pk}, title={self.title[:50] if self.title else ''})"

    def increment_views(self, amount: int = 1) -> int:
        """
        Atomically increment view_count by "amount" and refresh current instance.
        Returns the updated view_count.
        """
        amount = max(int(amount or 0), 0)
        if amount == 0:
            return int(self.view_count)
        Listing.objects.filter(pk=self.pk).update(view_count=F('view_count') + amount)
        self.refresh_from_db(fields=['view_count'])
        return int(self.view_count)


class Comment(models.Model):
    """
    Comment for a listing. If deleted=True, content remains in DB but must be
    masked for clients.
    """

    PLACEHOLDER_DELETED = '[deleted]'

    listing = models.ForeignKey('api.Listing', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(blank=False)
    edited = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CommentQuerySet.as_manager()

    class Meta:
        indexes = [
            Index(fields=['listing', '-created_at']),
            Index(fields=['deleted']),
            Index(fields=['likes_count']),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Comment(id={self.pk}, listing_id={self.listing_id}, user_id={self.user_id})"

    @property
    def masked_content(self) -> str:
        return self.PLACEHOLDER_DELETED if self.deleted else self.content


class CommentLike(models.Model):
    """
    Like for a comment. Unique per (user, comment).
    Maintains Comment.likes_count using atomic F-expressions on create/delete/update.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey('api.Comment', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'comment'], name='unique_user_comment_like'),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"CommentLike(id={self.pk}, comment_id={self.comment_id}, user_id={self.user_id})"

    def save(self, *args, **kwargs):
        is_create = self.pk is None
        old_comment_id = None
        if not is_create:
            try:
                old = CommentLike.objects.get(pk=self.pk)
                old_comment_id = old.comment_id
            except CommentLike.DoesNotExist:
                old_comment_id = None
        result = super().save(*args, **kwargs)
        if is_create:
            Comment.objects.filter(pk=self.comment_id).update(likes_count=F('likes_count') + 1)
        else:
            if old_comment_id and old_comment_id != self.comment_id:
                Comment.objects.filter(pk=old_comment_id).update(likes_count=F('likes_count') - 1)
                Comment.objects.filter(pk=self.comment_id).update(likes_count=F('likes_count') + 1)
        return result

    def delete(self, *args, **kwargs):
        comment_id = self.comment_id
        result = super().delete(*args, **kwargs)
        if comment_id:
            Comment.objects.filter(pk=comment_id, likes_count__gt=0).update(likes_count=F('likes_count') - 1)
        return result


class BannedPattern(models.Model):
    """
    Patterns used to validate comments. If is_regex=True, pattern is treated as
    a regular expression (case-insensitive). Otherwise, simple substring match
    (case-insensitive).
    """

    pattern = models.CharField(max_length=255)
    is_regex = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BannedPatternQuerySet.as_manager()

    class Meta:
        ordering = ['-active', '-updated_at']
        indexes = [
            Index(fields=['active']),
            Index(fields=['is_regex']),
        ]

    def __str__(self) -> str:
        flag = 'regex' if self.is_regex else 'plain'
        state = 'active' if self.active else 'inactive'
        return f"BannedPattern(id={self.pk}, {flag}, {state}): {self.pattern}"

    def matches(self, text: str) -> bool:
        if not text:
            return False
        if self.is_regex:
            try:
                return re.search(self.pattern, text, flags=re.IGNORECASE) is not None
            except re.error:
                # Fallback to substring if regex is invalid
                return self.pattern.lower() in text.lower()
        return self.pattern.lower() in text.lower()
