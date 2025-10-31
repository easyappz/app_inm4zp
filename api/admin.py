from django.contrib import admin
from .models import Listing, Comment, CommentLike, BannedPattern


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'avito_url', 'price', 'view_count', 'created_at', 'updated_at',
    )
    search_fields = ('title', 'avito_url', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    actions = ('reset_view_count',)

    @admin.action(description='Reset view_count to 0')
    def reset_view_count(self, request, queryset):
        updated = queryset.update(view_count=0)
        self.message_user(request, f'Reset view_count for {updated} listings.')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'listing', 'user', 'short_content', 'likes_count', 'deleted', 'edited', 'created_at', 'updated_at',
    )
    search_fields = (
        'content', 'user__username', 'listing__title', 'listing__avito_url',
    )
    list_filter = ('deleted', 'edited', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'likes_count')
    actions = ('mark_deleted', 'restore_deleted')

    @admin.display(description='Content (short)')
    def short_content(self, obj: Comment) -> str:
        text = obj.masked_content
        return (text[:75] + '…') if len(text) > 75 else text

    @admin.action(description='Mark selected comments as deleted')
    def mark_deleted(self, request, queryset):
        updated = queryset.update(deleted=True)
        self.message_user(request, f'Marked {updated} comments as deleted.')

    @admin.action(description='Restore selected comments (deleted=False)')
    def restore_deleted(self, request, queryset):
        updated = queryset.update(deleted=False)
        self.message_user(request, f'Restored {updated} comments.')


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'user', 'created_at')
    search_fields = ('comment__content', 'user__username')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(BannedPattern)
class BannedPatternAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'pattern', 'is_regex', 'active', 'updated_at', 'created_at',
    )
    search_fields = ('pattern', 'description')
    list_filter = ('active', 'is_regex', 'updated_at', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    actions = ('activate_patterns', 'deactivate_patterns')

    @admin.action(description='Activate selected patterns')
    def activate_patterns(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f'Activated {updated} patterns.')

    @admin.action(description='Deactivate selected patterns')
    def deactivate_patterns(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f'Deactivated {updated} patterns.')
