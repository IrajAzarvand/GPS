from django.contrib import admin
from .models import AdminNotification, SystemSetting


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'title', 'message', 'notification_type', 'is_read')
        }),
        ('Action', {
            'fields': ('action_url', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notification(s) marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'is_public', 'updated_at')
    list_filter = ('is_public', 'updated_at')
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Setting Details', {
            'fields': ('key', 'value', 'description', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )








