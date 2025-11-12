from django.contrib import admin
from .models import DeviceType, Protocol, Device


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'connectivity_type', 'battery_life_hours', 'supports_geofencing', 'is_active')
    list_filter = ('is_active', 'supports_geofencing', 'supports_real_time_tracking', 'has_sos_button')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Specifications', {
            'fields': ('battery_life_hours', 'connectivity_type', 'waterproof_rating', 'operating_temperature')
        }),
        ('Features', {
            'fields': ('supports_geofencing', 'supports_real_time_tracking', 'has_sos_button', 'has_motion_sensor')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    list_display = ('name', 'protocol_type', 'default_port', 'requires_authentication', 'is_active')
    list_filter = ('protocol_type', 'requires_authentication', 'supports_encryption', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'protocol_type', 'description', 'is_active')
        }),
        ('Technical Details', {
            'fields': ('default_port', 'requires_authentication', 'supports_encryption', 'update_frequency_seconds')
        }),
        ('Message Format', {
            'fields': ('message_format',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'imei', 'device_id', 'user', 'device_type', 'status', 'last_location_time', 'expires_at')
    list_filter = ('status', 'device_type', 'protocol', 'activated_at', 'expires_at')
    search_fields = ('name', 'imei', 'device_id', 'serial_number', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'activated_at')

    fieldsets = (
        ('Device Information', {
            'fields': ('user', 'product', 'device_type', 'name')
        }),
        ('Identification', {
            'fields': ('imei', 'device_id', 'serial_number', 'activation_code')
        }),
        ('Technical Details', {
            'fields': ('protocol', 'firmware_version', 'config_settings')
        }),
        ('Status & Location', {
            'fields': ('status', 'last_location_lat', 'last_location_lng', 'last_location_time', 'battery_level')
        }),
        ('Subscription', {
            'fields': ('activated_at', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_devices', 'deactivate_devices']

    def activate_devices(self, request, queryset):
        for device in queryset.filter(status='inactive'):
            device.activate()
        self.message_user(request, f"{queryset.count()} device(s) activated.")
    activate_devices.short_description = "Activate selected devices"

    def deactivate_devices(self, request, queryset):
        for device in queryset.filter(status='active'):
            device.deactivate()
        self.message_user(request, f"{queryset.count()} device(s) deactivated.")
    deactivate_devices.short_description = "Deactivate selected devices"
