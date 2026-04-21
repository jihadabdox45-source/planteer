from django.contrib import admin
from .models import Plant, Comment, Rating


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    
    list_display = [
        'name', 
        'scientific_name', 
        'category', 
        'is_edible', 
        'comment_count',
        'created_at'
    ]
    list_filter = ['category', 'is_edible', 'created_at']
    search_fields = ['name', 'scientific_name', 'description']
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'scientific_name', 'category', 'is_edible')
        }),
        ('Details', {
            'fields': ('description', 'image_url')
        }),
        ('Care Requirements', {
            'fields': ('sunlight', 'water_needs')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'plant', 'content_preview', 'created_at']
    list_filter = ['created_at', 'plant']
    search_fields = ['name', 'content', 'plant__name']
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('plant', 'name', 'content')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        max_length = 50
        if len(obj.content) > max_length:
            return f'{obj.content[:max_length]}...'
        return obj.content
    content_preview.short_description = 'Comment Preview'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'plant', 'score', 'created_at']
    list_filter = ['score', 'created_at', 'plant']
    search_fields = ['name', 'plant__name']
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Rating Information', {
            'fields': ('plant', 'name', 'score')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
