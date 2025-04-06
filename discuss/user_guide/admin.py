from django.contrib import admin
from .models import UserGuideStep

@admin.register(UserGuideStep)
class UserGuideStepAdmin(admin.ModelAdmin):
    list_display = ('guide_type', 'order', 'title')
    list_filter = ('guide_type',)
    search_fields = ('title', 'content')
    ordering = ('guide_type', 'order')
    fieldsets = (
        (None, {
            'fields': ('guide_type', 'order', 'title', 'content')
        }),
        ('Display Options', {
            'fields': ('element_selector', 'position'),
            'classes': ('collapse',),
        }),
    )