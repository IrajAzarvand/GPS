# GPS-Specific Models Design for GPS Store E-commerce Site

## Overview

This document outlines additional Django models for GPS device management, subscriptions, tracking, and alerts. These models integrate with the existing e-commerce schema (UserProfile, Address, Category, Product, etc.) to support real-time tracking, subscription management, and Neshan API integration. Models are designed for PostgreSQL with JSON fields for flexible configurations.

## 1. GPS Device Type Model (gps_devices app)

Defines different types of GPS devices available in the store.

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class DeviceType(models.Model):
    DEVICE_TYPES = [
        ('vehicle', 'Vehicle Tracker'),
        ('personal', 'Personal Tracker'),
        ('pet', 'Pet Tracker'),
        ('asset', 'Asset Tracker'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=DEVICE_TYPES)
    description = models.TextField(blank=True)
    battery_life_hours = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8760)]  # Max 1 year
    )
    connectivity_options = models.JSONField(default=list)  # ['GPS', 'GSM', 'WiFi', 'Bluetooth']
    supported_protocols = models.JSONField(default=list)  # ['MQTT', 'HTTP', 'TCP', 'SMS']
    features = models.JSONField(default=dict)  # {'geofencing': True, 'real_time': True, 'sos_button': False}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"

    class Meta:
        verbose_name = 'Device Type'
        verbose_name_plural = 'Device Types'
        ordering = ['category', 'name']
```

## 2. Communication Protocol Model (gps_devices app)

Manages different communication protocols for GPS devices.

```python
class Protocol(models.Model):
    PROTOCOL_TYPES = [
        ('mqtt', 'MQTT'),
        ('http', 'HTTP/HTTPS'),
        ('tcp', 'TCP'),
        ('sms', 'SMS'),
    ]

    name = models.CharField(max_length=50, unique=True)
    protocol_type = models.CharField(max_length=10, choices=PROTOCOL_TYPES)
    description = models.TextField(blank=True)
    port = models.PositiveIntegerField(null=True, blank=True)
    requires_authentication = models.BooleanField(default=True)
    data_format = models.CharField(max_length=50, default='JSON')  # JSON, XML, Binary
    encryption_supported = models.BooleanField(default=False)
    real_time_capable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_protocol_type_display()})"

    class Meta:
        verbose_name = 'Communication Protocol'
        verbose_name_plural = 'Communication Protocols'
```

## 3. GPS Device Model (gps_devices app)

Represents individual GPS devices registered to users.

```python
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Device(models.Model):
    STATUS_CHOICES = [
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('maintenance', 'Maintenance'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_type = models.ForeignKey(DeviceType, on_delete=models.PROTECT)
    protocol = models.ForeignKey(Protocol, on_delete=models.PROTECT)
    imei = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{15}$', message="IMEI must be 15 digits.")]
    )
    serial_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, help_text="User-defined device name")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    firmware_version = models.CharField(max_length=20, blank=True)
    api_key = models.CharField(max_length=64, unique=True, blank=True, null=True)
    configuration = models.JSONField(default=dict)  # Device-specific settings
    last_seen = models.DateTimeField(null=True, blank=True)
    battery_level = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(100)])
    registered_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.imei}) - {self.user.username}"

    def activate(self):
        """Activate the device and set activation timestamp."""
        from django.utils import timezone
        self.status = 'active'
        self.activated_at = timezone.now()
        self.save()

    def deactivate(self):
        """Deactivate the device."""
        self.status = 'inactive'
        self.save()

    def is_online(self):
        """Check if device is online based on last seen timestamp."""
        from django.utils import timezone
        if not self.last_seen:
            return False
        return (timezone.now() - self.last_seen).seconds < 300  # 5 minutes

    def get_subscription(self):
        """Get active subscription for this device."""
        return self.subscriptions.filter(status='active').first()

    class Meta:
        verbose_name = 'GPS Device'
        verbose_name_plural = 'GPS Devices'
        ordering = ['-registered_at']
        unique_together = ('user', 'imei')
```

## 4. Subscription Plan Model (subscriptions app)

Defines annual subscription plans for GPS services.

```python
class SubscriptionPlan(models.Model):
    PLAN_TYPES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]

    name = models.CharField(max_length=100, unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    price_per_year = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=dict)  # {'real_time_tracking': True, 'geofencing': 5, 'alerts': True}
    max_devices = models.PositiveIntegerField(default=1)
    data_retention_days = models.PositiveIntegerField(default=365)
    api_rate_limit = models.PositiveIntegerField(default=1000)  # requests per hour
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.price_per_year} IRR/year"

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['price_per_year']
```

## 5. Subscription Model (subscriptions app)

Manages user subscriptions to GPS services.

```python
class Subscription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    devices = models.ManyToManyField(Device, related_name='subscriptions', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField()
    auto_renew = models.BooleanField(default=True)
    payment_method = models.CharField(max_length=50, blank=True)  # Reference to payment method
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"

    def is_active(self):
        """Check if subscription is currently active."""
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date

    def days_remaining(self):
        """Calculate days remaining in subscription."""
        from django.utils import timezone
        today = timezone.now().date()
        if self.end_date < today:
            return 0
        return (self.end_date - today).days

    def renew(self):
        """Renew subscription for another year."""
        from dateutil.relativedelta import relativedelta
        self.end_date = self.end_date + relativedelta(years=1)
        self.save()

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
        unique_together = ('user', 'plan', 'start_date')  # Prevent duplicate active subscriptions
```

## 6. Location Data Model (tracking app)

Stores GPS location data from devices.

```python
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point

class LocationData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='locations')
    timestamp = models.DateTimeField()
    location = gis_models.PointField(geography=True)  # PostGIS Point field
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # km/h
    heading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # degrees
    accuracy = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # meters
    battery_level = models.PositiveIntegerField(null=True, blank=True)
    signal_strength = models.PositiveIntegerField(null=True, blank=True)  # 0-100
    raw_data = models.JSONField(default=dict)  # Store original protocol data
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # Ensure location point matches lat/lng
        if not self.location and self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude), srid=4326)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Location Data'
        verbose_name_plural = 'Location Data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            gis_models.GistIndex(fields=['location']),
        ]
```

## 7. Geofence Model (tracking app)

Defines geographical boundaries for alerts.

```python
class Geofence(models.Model):
    GEOFENCE_TYPES = [
        ('circle', 'Circle'),
        ('polygon', 'Polygon'),
        ('rectangle', 'Rectangle'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='geofences')
    name = models.CharField(max_length=100)
    geofence_type = models.CharField(max_length=20, choices=GEOFENCE_TYPES, default='circle')
    center_point = gis_models.PointField(geography=True, null=True, blank=True)  # For circle type
    radius_meters = models.PositiveIntegerField(null=True, blank=True)  # For circle type
    boundary = gis_models.PolygonField(geography=True, null=True, blank=True)  # For polygon/rectangle
    address = models.CharField(max_length=255, blank=True)  # Human-readable address
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def contains_point(self, latitude, longitude):
        """Check if a point is inside the geofence."""
        from django.contrib.gis.geos import Point
        point = Point(float(longitude), float(latitude), srid=4326)
        if self.geofence_type == 'circle' and self.center_point and self.radius_meters:
            return self.center_point.distance(point) * 100000 <= self.radius_meters  # Approximate meters
        elif self.boundary:
            return self.boundary.contains(point)
        return False

    class Meta:
        verbose_name = 'Geofence'
        verbose_name_plural = 'Geofences'
        ordering = ['-created_at']
```

## 8. Alert Model (tracking app)

Manages alerts triggered by GPS events.

```python
class Alert(models.Model):
    ALERT_TYPES = [
        ('geofence_enter', 'Geofence Enter'),
        ('geofence_exit', 'Geofence Exit'),
        ('speeding', 'Speeding'),
        ('battery_low', 'Battery Low'),
        ('device_offline', 'Device Offline'),
        ('sos', 'SOS Button'),
        ('tampering', 'Device Tampering'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    message = models.TextField()
    location = gis_models.PointField(geography=True, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geofence = models.ForeignKey(Geofence, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    metadata = models.JSONField(default=dict)  # Additional alert-specific data
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.device.name} ({self.created_at})"

    def resolve(self, user):
        """Mark alert as resolved."""
        from django.utils import timezone
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()

    class Meta:
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['device', '-created_at']),
            models.Index(fields=['is_read', 'is_resolved']),
        ]
```

## Integration with Existing Models

### Product Model Extensions

Add GPS-specific fields to the existing Product model:

```python
# In products/models.py, extend Product model
class Product(models.Model):
    # ... existing fields ...

    # GPS-specific fields
    is_gps_device = models.BooleanField(default=False)
    device_type = models.ForeignKey('gps_devices.DeviceType', on_delete=models.SET_NULL, null=True, blank=True)
    subscription_required = models.BooleanField(default=False)
    compatible_plans = models.ManyToManyField('subscriptions.SubscriptionPlan', blank=True)

    # ... existing methods ...
```

### Order Model Extensions

Link orders to device activation:

```python
# In orders/models.py, extend Order model
class Order(models.Model):
    # ... existing fields ...

    # GPS-specific fields
    activates_devices = models.BooleanField(default=False)
    device_imei_list = models.JSONField(default=list, blank=True)  # List of IMEIs to activate

    # ... existing methods ...
```

## Neshan API Integration Fields

Add API configuration models:

```python
# In tracking/models.py or a new api app
class NeshanAPIConfig(models.Model):
    api_key = models.CharField(max_length=100, unique=True)
    api_secret = models.CharField(max_length=100)
    rate_limit = models.PositiveIntegerField(default=1000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Neshan API Config'
        verbose_name_plural = 'Neshan API Configs'
```

## Database Schema Summary

The GPS models extend the existing schema with 8 new models across 3 apps:

- **gps_devices**: DeviceType (4), Protocol (4), Device (23)
- **subscriptions**: SubscriptionPlan (9), Subscription (10)
- **tracking**: LocationData (13), Geofence (10), Alert (15)

Total new fields: ~88 fields plus relationships.

Key relationships:

- Device links to User, DeviceType, Protocol
- Subscription links to User, Plan, Devices (ManyToMany)
- LocationData links to Device
- Geofence links to User
- Alert links to Device, Geofence (optional)

Constraints ensure data integrity with foreign keys, unique constraints, and validators. Methods provide business logic for device management, subscription handling, geofencing, and alert processing. The schema supports real-time tracking, subscription management, and Neshan API integration as specified.
