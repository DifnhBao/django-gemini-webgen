from django.contrib import admin

from .models import GeneratedWebsite


@admin.register(GeneratedWebsite)
class GeneratedWebsiteAdmin(admin.ModelAdmin):
    list_display = ('topic', 'user', 'created_at')
    search_fields = ('topic', 'user__username')
    readonly_fields = ('created_at',)
