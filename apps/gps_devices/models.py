from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from apps.products.models import Product


class DeviceType(models.Model):
    """
    Types of GPS devices (vehicle, personal, pet, asset)
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    # Device specifications
    battery_life_hours = models.PositiveIntegerField(help_text="Battery life in hours")
    connectivity_type = models.CharField(max_length=50, help_text="GPS, GSM, etc.")
    waterproof_rating = models.CharField(max_length=20, blank=True)
    operating_temperature = models.CharField(max_length=20, blank=True, help_text="e.g., -20°C to +60°C")

    # Features
    supports_geofencing = models.BooleanField(default=True)
    supports_real_time_tracking = models.BooleanField(default=True)
    has_sos_button = models.BooleanField(default=False)
    has_motion_sensor = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Device Type'
        verbose_name_plural = 'Device Types'


class Protocol(models.Model):
    """
    Communication protocols for GPS devices
    """
    PROTOCOL_TYPES = [
        ('mqtt', 'MQTT'),
        ('http', 'HTTP'),
        ('tcp', 'TCP'),
        ('sms', 'SMS'),
    ]

    name = models.CharField(max_length=50, unique=True)
    protocol_type = models.CharField(max_length=10, choices=PROTOCOL_TYPES)
    description = models.TextField(blank=True)

    # Protocol settings
    default_port = models.PositiveIntegerField(null=True, blank=True)
    requires_authentication = models.BooleanField(default=True)
    supports_encryption = models.BooleanField(default=False)

    # Message format
    message_format = models.JSONField(default=dict, help_text="JSON schema for message format")
    update_frequency_seconds = models.PositiveIntegerField(default=60, help_text="How often device sends updates")
    dynamic_config = models.JSONField(default=dict, blank=True, help_text="Dynamic settings for the protocol (e.g., server address, port, certificates)")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.protocol_type})"

    class Meta:
        verbose_name = 'Protocol'
        verbose_name_plural = 'Protocols'


class Device(models.Model):
    """
    Individual GPS devices registered to users
    """
    STATUS_CHOICES = [
        ('inactive', 'غیرفعال'),
        ('active', 'فعال'),
        ('suspended', 'معلق'),
        ('maintenance', 'در حال تعمیر'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gps_devices')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='devices')
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)

    # Device identification
    imei = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\d{15}$', message="IMEI must be 15 digits")]
    )
    device_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Alternative device identifier"
    )
    serial_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, help_text="User-defined device name")

    # Device configuration
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE)
    firmware_version = models.CharField(max_length=20, blank=True)
    config_settings = models.JSONField(default=dict, help_text="Device-specific configuration")
    port_config = models.JSONField(default=dict, blank=True, help_text="Dynamic port settings (e.g., dedicated port or range)")
    assigned_port = models.PositiveIntegerField(null=True, blank=True, help_text="Assigned port for the device")

    # Status and location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    last_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_time = models.DateTimeField(null=True, blank=True)
    battery_level = models.PositiveIntegerField(null=True, blank=True, help_text="Battery percentage")

    # Activation
    activation_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Subscription expiry")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        identifier = self.imei or self.device_id or "No ID"
        return f"{self.name} ({identifier})"

    def activate(self):
        """Activate the device"""
        from django.utils import timezone
        self.status = 'active'
        self.activated_at = timezone.now()
        self.save()

    def deactivate(self):
        """Deactivate the device"""
        self.status = 'inactive'
        self.save()

    def is_active_subscription(self):
        """Check if device has active subscription"""
        from django.utils import timezone
        return self.expires_at and self.expires_at > timezone.now() and self.status == 'active'

    def clean(self):
        """Validate that at least one identifier is provided"""
        if not self.imei and not self.device_id:
            raise ValidationError("Either IMEI or Device ID must be provided.")

    def update_location(self, lat, lng, timestamp=None):
        """Update device location"""
        from django.utils import timezone
        self.last_location_lat = lat
        self.last_location_lng = lng
        self.last_location_time = timestamp or timezone.now()
        self.save()

    class Meta:
        verbose_name = 'GPS Device'
        verbose_name_plural = 'GPS Devices'
        ordering = ['-created_at']


class RawGPSData(models.Model):
    """
    Stores raw GPS data received from devices before processing
    """
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='raw_data', null=True, blank=True)
    protocol = models.ForeignKey(Protocol, on_delete=models.CASCADE, null=True, blank=True)
    raw_data = models.TextField(help_text="Raw data received from the device")
    received_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Source IP address")
    processed = models.BooleanField(default=False, help_text="Whether this data has been processed")
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, help_text="Error message if processing failed")

    def __str__(self):
        device_name = self.device.name if self.device else "Unknown Device"
        return f"Raw data from {device_name} at {self.received_at}"

    def mark_processed(self):
        """Mark the data as processed"""
        from django.utils import timezone
        self.processed = True
        self.processed_at = timezone.now()
        self.save()

    def mark_error(self, error_msg):
        """Mark processing as failed with error message"""
        from django.utils import timezone
        self.processed = True
        self.processed_at = timezone.now()
        self.error_message = error_msg
        self.save()

    class Meta:
        verbose_name = 'Raw GPS Data'
        verbose_name_plural = 'Raw GPS Data'
        ordering = ['-received_at']
        indexes = [
            models.Index(fields=['device', '-received_at']),
            models.Index(fields=['processed', 'received_at']),
        ]
