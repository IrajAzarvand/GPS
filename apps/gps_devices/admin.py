import logging
from django.contrib import admin
from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import DeviceType, Protocol, Device, RawGPSData

logger = logging.getLogger(__name__)


class DateRangeFilter(admin.SimpleListFilter):
    title = 'Date Range'
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('week', 'Past 7 days'),
            ('month', 'This month'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'today':
            return queryset.filter(received_at__date=now.date())
        elif self.value() == 'yesterday':
            yesterday = now.date() - timedelta(days=1)
            return queryset.filter(received_at__date=yesterday)
        elif self.value() == 'week':
            week_ago = now - timedelta(days=7)
            return queryset.filter(received_at__gte=week_ago)
        elif self.value() == 'month':
            return queryset.filter(received_at__year=now.year, received_at__month=now.month)


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


@admin.register(RawGPSData)
class RawGPSDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'protocol', 'received_at', 'processed', 'ip_address')
    list_filter = ('protocol', 'processed', 'device', DateRangeFilter)
    search_fields = ('raw_data', 'ip_address')
    readonly_fields = ('received_at', 'processed_at', 'error_message')

    def get_queryset(self, request):
        logger.info("RawGPSDataAdmin: Getting queryset")
        try:
            qs = super().get_queryset(request)
            logger.info(f"RawGPSDataAdmin: Queryset count: {qs.count()}")
            return qs
        except Exception as e:
            logger.error(f"RawGPSDataAdmin: Error in get_queryset: {e}")
            raise

    fieldsets = (
        ('Data Information', {
            'fields': ('device', 'protocol', 'received_at', 'ip_address')
        }),
        ('Raw Data', {
            'fields': ('raw_data',),
            'classes': ('collapse',)
        }),
        ('Processing Status', {
            'fields': ('processed', 'processed_at', 'error_message')
        }),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'raw_data':
            kwargs['widget'] = forms.Textarea(attrs={'readonly': True, 'rows': 10, 'cols': 80})
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)
