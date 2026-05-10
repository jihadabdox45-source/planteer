from django.contrib import admin
from .models import Plant, Comment, Rating, Favorite, Category, PlantImage, Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'plants_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Country Information', {
            'fields': ('name', 'flag')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'plants_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('name',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class PlantImageInline(admin.TabularInline):
    model = PlantImage
    extra = 1
    fields = ['image_url', 'caption', 'is_primary']
    readonly_fields = ['created_at']


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    
    list_display = [
        'name', 
        'scientific_name', 
        'category', 
        'is_edible', 
        'comment_count',
        'images_count',
        'created_at'
    ]
    list_filter = ['category', 'is_edible', 'countries', 'created_at']
    search_fields = ['name', 'scientific_name', 'description']
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'views_count']
    inlines = [PlantImageInline]
    filter_horizontal = ['countries']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'scientific_name', 'category', 'countries', 'is_edible')
        }),
        ('Details', {
            'fields': ('description', 'image_url')
        }),
        ('Care Requirements', {
            'fields': ('sunlight', 'water_needs')
        }),
        ('Statistics', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'
    
    def images_count(self, obj):
        return obj.images.count()
    images_count.short_description = 'Images'


@admin.register(PlantImage)
class PlantImageAdmin(admin.ModelAdmin):
    list_display = ['plant', 'caption', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at', 'plant']
    search_fields = ['plant__name', 'caption']
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('plant', 'image_url', 'caption', 'is_primary')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    
    list_display = ['get_author_name', 'plant', 'content_preview', 'created_at']
    list_filter = ['created_at', 'plant']
    search_fields = ['name', 'user__username', 'content', 'plant__name']
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('plant', 'user', 'name', 'content')
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
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    get_author_name.short_description = 'Author'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    
    list_display = ['get_author_name', 'plant', 'score', 'created_at']
    list_filter = ['score', 'created_at', 'plant']
    search_fields = ['name', 'user__username', 'plant__name']
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Rating Information', {
            'fields': ('plant', 'user', 'name', 'score')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_author_name(self, obj):
        return obj.get_author_name()
    get_author_name.short_description = 'Author'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    
    list_display = ['user', 'plant', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username', 'plant__name']
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Favorite Information', {
            'fields': ('user', 'plant')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
