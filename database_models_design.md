# Database Models Design for GPS Store E-commerce Site

## Overview

This document outlines the Django models for the GPS Store e-commerce site, based on the architecture plan. Models are designed to support user management, product catalog, shopping cart, orders, payments, and reviews. All models use Django's ORM with PostgreSQL as the database.

## 1. User Profile Model (accounts app)

Extends Django's built-in User model for additional profile information.

```python
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
```

## 2. Address Model (accounts app)

Stores user addresses for shipping and billing.

```python
class Address(models.Model):
    ADDRESS_TYPES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='shipping')
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Iran')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address_type} address for {self.user.username}"

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        unique_together = ('user', 'address_type', 'is_default')  # Prevent multiple defaults per type
```

## 3. Category Model (products app)

Categorizes GPS products (vehicle, personal, pet, asset trackers).

```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
```

## 4. Product Model (products app)

Represents GPS products with details and inventory.

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in kg
    dimensions = models.CharField(max_length=100, blank=True)  # e.g., "10x5x2 cm"
    battery_life = models.CharField(max_length=100, blank=True)  # e.g., "24 hours"
    connectivity = models.CharField(max_length=100, blank=True)  # e.g., "GPS, GSM"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_discounted_price(self):
        return self.discount_price if self.discount_price else self.price

    def is_in_stock(self):
        return self.stock_quantity > 0

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
```

## 5. Product Image Model (products app)

Handles multiple images per product.

```python
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['order']
        unique_together = ('product', 'is_primary')  # Only one primary image per product
```

## 6. Review Model (products app)

Stores product reviews and ratings.

```python
class Review(models.Model):
    RATINGS = [(i, i) for i in range(1, 6)]  # 1 to 5 stars

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATINGS)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ('product', 'user')  # One review per user per product
        ordering = ['-created_at']
```

## 7. Cart Model (cart app)

Session-based shopping cart.

```python
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username if self.user else 'Anonymous'}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
```

## 8. Cart Item Model (cart app)

Items in the shopping cart.

```python
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.product.get_discounted_price() * self.quantity

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')
```

## 9. Order Model (orders app)

Manages customer orders.

```python
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='shipping_orders')
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='billing_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD{self.pk:06d}" if self.pk else "TEMP"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
```

## 10. Order Item Model (orders app)

Items within an order.

```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_number}"

    def get_total_price(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
```

## 11. Payment Model (payments app)

Handles payment transactions with support for multiple gateways and methods.

```python
class Payment(models.Model):
    PAYMENT_METHODS = [
        ('zarinpal', 'Zarinpal Gateway'),
        ('mellat', 'Mellat Bank Gateway'),
        ('saderat', 'Saderat Bank Gateway'),
        ('parsian', 'Parsian Bank Gateway'),
        ('card_to_card', 'Card-to-Card Transfer'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Bank's reference ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)

    # Gateway-specific fields
    zarinpal_authority = models.CharField(max_length=100, blank=True, null=True)
    zarinpal_ref_id = models.CharField(max_length=100, blank=True, null=True)
    bank_token = models.CharField(max_length=200, blank=True, null=True)  # For bank gateway tokens

    # Card-to-card specific fields
    card_transfer = models.OneToOneField('CardToCardTransfer', on_delete=models.SET_NULL, null=True, blank=True, related_name='payment')

    # Additional metadata
    gateway_response = models.JSONField(default=dict, blank=True)  # Store full gateway response
    failure_reason = models.TextField(blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.order_number} via {self.get_payment_method_display()}"

    def mark_completed(self, transaction_id=None, gateway_ref=None):
        """Mark payment as completed with optional transaction details."""
        from django.utils import timezone
        self.status = 'completed'
        self.payment_date = timezone.now()
        if transaction_id:
            self.transaction_id = transaction_id
        if gateway_ref:
            self.gateway_transaction_id = gateway_ref
        self.save()

    def mark_failed(self, reason=None):
        """Mark payment as failed with reason."""
        self.status = 'failed'
        if reason:
            self.failure_reason = reason
        self.save()

    def can_retry(self):
        """Check if payment can be retried."""
        return self.status in ['failed', 'pending'] and self.retry_count < 3

    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1
        self.save()

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'payment_method']),
            models.Index(fields=['created_at']),
        ]
```

## 12. Card-to-Card Transfer Model (payments app)

Handles manual card-to-card transfer verifications.

```python
class CardToCardTransfer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='card_transfer')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_transfers')

    # Admin card details (should be configurable)
    admin_card_number = models.CharField(max_length=16, help_text="Admin's card number for transfers")
    admin_card_holder = models.CharField(max_length=100, help_text="Admin's card holder name")
    admin_bank_name = models.CharField(max_length=50, help_text="Admin's bank name")

    # User-submitted transfer details
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=2)
    user_card_number = models.CharField(max_length=16, blank=True, null=True)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)  # Bank transaction ID
    transfer_date = models.DateTimeField(blank=True, null=True)
    transfer_time = models.TimeField(blank=True, null=True)
    user_notes = models.TextField(blank=True, null=True)

    # Verification details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_transfers')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True, null=True)

    # Expiration
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Card Transfer for Order {self.payment.order.order_number}"

    def verify(self, admin_user, notes=None):
        """Mark transfer as verified by admin."""
        from django.utils import timezone
        self.status = 'verified'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        if notes:
            self.verification_notes = notes
        self.save()
        # Mark associated payment as completed
        self.payment.mark_completed()

    def reject(self, admin_user, notes=None):
        """Reject the transfer."""
        from django.utils import timezone
        self.status = 'rejected'
        self.verified_by = admin_user
        self.verified_at = timezone.now()
        if notes:
            self.verification_notes = notes
        self.save()
        # Mark associated payment as failed
        self.payment.mark_failed('Transfer rejected by admin')

    def is_expired(self):
        """Check if transfer request has expired."""
        from django.utils import timezone
        return timezone.now() > self.expires_at

    class Meta:
        verbose_name = 'Card-to-Card Transfer'
        verbose_name_plural = 'Card-to-Card Transfers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'expires_at']),
        ]
```

## Database Schema Summary

The database schema includes 11 models across 5 Django apps:

- **accounts**: UserProfile, Address (user management and addresses)
- **products**: Category, Product, ProductImage, Review (product catalog and reviews)
- **cart**: Cart, CartItem (shopping cart functionality)
- **orders**: Order, OrderItem (order management)
- **payments**: Payment (payment processing)

Key relationships:

- One-to-One: User-Profile, Order-Payment
- One-to-Many: User-Addresses/Orders, Category-Products, Product-Images/Reviews, Cart-CartItems, Order-OrderItems
- Many-to-Many: None (handled through intermediate models)

Constraints ensure data integrity (unique fields, foreign keys, validators). Methods provide business logic for pricing, stock checks, and totals. The schema supports all features from the architecture plan including product listings, user profiles, cart management, order tracking, and payment processing.
