from django.contrib import admin

from .models import Post, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
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
