from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avito_url', models.URLField(db_index=True, unique=True)),
                ('title', models.CharField(max_length=512)),
                ('image_url', models.URLField(blank=True, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('description', models.TextField(blank=True)),
                ('view_count', models.PositiveIntegerField(db_index=True, default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-view_count', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BannedPattern',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pattern', models.CharField(max_length=255)),
                ('is_regex', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-active', '-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('edited', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
                ('likes_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='api.listing')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='api.comment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='listing',
            index=models.Index(fields=['view_count'], name='api_listin_view_co_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['listing', '-created_at'], name='api_comme_listing__idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['deleted'], name='api_comme_deleted_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['likes_count'], name='api_comme_likes_co_idx'),
        ),
        migrations.AddIndex(
            model_name='bannedpattern',
            index=models.Index(fields=['active'], name='api_banned_active_idx'),
        ),
        migrations.AddIndex(
            model_name='bannedpattern',
            index=models.Index(fields=['is_regex'], name='api_banned_is_regex_idx'),
        ),
        migrations.AddConstraint(
            model_name='commentlike',
            constraint=models.UniqueConstraint(fields=('user', 'comment'), name='unique_user_comment_like'),
        ),
    ]
