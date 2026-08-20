from django import forms
from django.contrib import admin
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Article, DailyVisitor, Post, Release, SiteSettings, Tag, VisitorCountSnapshot


@admin.register(VisitorCountSnapshot)
class VisitorCountSnapshotAdmin(admin.ModelAdmin):
    list_display = ('checked_at', 'visitor_count')
    readonly_fields = ('checked_at', 'visitor_count')


@admin.register(DailyVisitor)
class DailyVisitorAdmin(admin.ModelAdmin):
    list_display = ('day', 'first_seen_at')
    list_filter = ('day',)
    readonly_fields = ('day', 'visitor_id', 'first_seen_at')
    search_fields = ('visitor_id',)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fields = ('site_icon',)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('legacy_top_image',)
        widgets = {
            'body': CKEditor5Widget(config_name='default'),
        }


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'is_published', 'published_at', 'updated_at')
    list_filter = ('is_published', 'tags')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'top_image', 'body', 'tags')}),
        ('Publishing', {'fields': ('is_published', 'published_at')}),
        ('History', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'body': CKEditor5Widget(config_name='default'),
        }


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title', 'subtitle', 'updated_at')
    search_fields = ('title', 'subtitle', 'body')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'subtitle', 'image', 'image_credit', 'body')}),
        ('History', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


class ReleaseAdminForm(forms.ModelForm):
    class Meta:
        model = Release
        fields = '__all__'
        exclude = ('legacy_image',)
        widgets = {
            'text': CKEditor5Widget(config_name='default'),
        }


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    form = ReleaseAdminForm
    list_display = ('title', 'artist', 'release_date', 'sort_order', 'link')
    search_fields = ('title', 'artist', 'text')
    list_editable = ('sort_order',)
