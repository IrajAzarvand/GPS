from django.contrib import admin
from .models import AdminNotification, SystemSetting
from apps.gps_devices.models import Device, DeviceType, Protocol
from apps.tracking.models import LocationData, Geofence, Alert


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


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'battery_life_hours', 'connectivity_type', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    readonly_fields = ('created_at',)

@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name', 'protocol_type', 'default_port', 'is_active', 'created_at')
    list_filter = ('protocol_type', 'is_active')
    search_fields = ('name',)
    readonly_fields = ('created_at',)

class LocationDataInline(admin.TabularInline):
    model = LocationData
    extra = 0
    fields = ('latitude', 'longitude', 'speed', 'timestamp')
    readonly_fields = ('latitude', 'longitude', 'speed', 'timestamp')
    ordering = ('-timestamp',)
    max_num = 10  # Limit to recent 10

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'device_type', 'status', 'last_location_lat', 'last_location_lng', 'last_location_time', 'battery_level', 'created_at')
    list_filter = ('status', 'device_type')
    search_fields = ('name', 'imei', 'device_id', 'serial_number', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LocationDataInline]

    fieldsets = (
        ('Identification', {
            'fields': ('user', 'product', 'device_type', 'name', 'imei', 'device_id', 'serial_number')
        }),
        ('Configuration', {
            'fields': ('protocol', 'firmware_version', 'config_settings', 'port_config', 'assigned_port')
        }),
        ('Status', {
            'fields': ('status', 'last_location_lat', 'last_location_lng', 'last_location_time', 'battery_level')
        }),
        ('Activation', {
            'fields': ('activation_code', 'activated_at', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LocationData)
class LocationDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'latitude', 'longitude', 'speed', 'altitude', 'heading', 'accuracy', 'timestamp', 'received_at')
    list_filter = ('device', 'timestamp')
    search_fields = ('device__name',)
    readonly_fields = ('received_at',)

@admin.register(Geofence)
class GeofenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'shape', 'is_active', 'created_at')
    list_filter = ('shape', 'is_active')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('device', 'alert_type', 'severity', 'is_read', 'is_resolved', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_read', 'is_resolved')
    search_fields = ('device__name', 'message')
    readonly_fields = ('created_at', 'resolved_at')
