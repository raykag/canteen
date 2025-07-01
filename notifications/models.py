from django.db import models
from django.conf import settings
import uuid

class NotificationCategory(models.Model):
    """Model for categorizing different types of notifications"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color_code = models.CharField(max_length=7, default='#007bff', help_text="Hex color code for UI display")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon class name")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification Category'
        verbose_name_plural = 'Notification Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Announcement(models.Model):
    """Model for general announcements to cooperative members"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    TARGET_AUDIENCE_CHOICES = [
        ('all', 'All Members'),
        ('farmers', 'Farmers Only'),
        ('staff', 'Staff Only'),
        ('admins', 'Administrators Only'),
        ('specific', 'Specific Users'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(NotificationCategory, on_delete=models.CASCADE, related_name='announcements')
    
    # Targeting and delivery
    target_audience = models.CharField(max_length=15, choices=TARGET_AUDIENCE_CHOICES, default='all')
    specific_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='targeted_announcements')
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    
    # Scheduling
    scheduled_time = models.DateTimeField(blank=True, null=True, help_text="When to publish/send the announcement")
    expires_at = models.DateTimeField(blank=True, null=True, help_text="When the announcement expires")
    
    # Delivery methods
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    show_on_dashboard = models.BooleanField(default=True)
    
    # Media attachments
    image = models.ImageField(upload_to='announcement_images/', blank=True, null=True)
    attachment = models.FileField(upload_to='announcement_attachments/', blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.status == 'published' and
            (not self.expires_at or self.expires_at > now)
        )
    
    @property
    def target_user_count(self):
        if self.target_audience == 'specific':
            return self.specific_users.count()
        elif self.target_audience == 'all':
            from users.models import User
            return User.objects.filter(is_active_member=True).count()
        elif self.target_audience == 'farmers':
            from users.models import User
            return User.objects.filter(role='farmer', is_active_member=True).count()
        elif self.target_audience == 'staff':
            from users.models import User
            return User.objects.filter(role='staff', is_active=True).count()
        elif self.target_audience == 'admins':
            from users.models import User
            return User.objects.filter(role='admin', is_active=True).count()
        return 0


class Notification(models.Model):
    """Model for individual notifications sent to specific users"""
    
    NOTIFICATION_TYPES = [
        ('announcement', 'Announcement'),
        ('loan_status', 'Loan Status Update'),
        ('equipment_allocation', 'Equipment Allocation'),
        ('payment_reminder', 'Payment Reminder'),
        ('maintenance_due', 'Maintenance Due'),
        ('system', 'System Notification'),
        ('custom', 'Custom Message'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    # Delivery tracking
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    # Additional data (JSON field for flexibility)
    extra_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.title} → {self.recipient.get_full_name()}"
    
    def mark_as_read(self):
        if not self.read_at:
            from django.utils import timezone
            self.read_at = timezone.now()
            self.status = 'read'
            self.save(update_fields=['read_at', 'status'])
    
    @property
    def is_read(self):
        return self.read_at is not None


class SMSLog(models.Model):
    """Model for logging SMS messages sent"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_phone = models.CharField(max_length=15)
    recipient_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sms_logs')
    message = models.TextField()
    
    # Provider details
    provider = models.CharField(max_length=50, default='africastalking')
    provider_message_id = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    cost = models.DecimalField(max_digits=6, decimal_places=4, blank=True, null=True, help_text="Cost in KES")
    
    # Related notification
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True, related_name='sms_logs')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    # Error details
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'
    
    def __str__(self):
        return f"SMS to {self.recipient_phone} - {self.get_status_display()}"


class EmailLog(models.Model):
    """Model for logging email messages sent"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('bounced', 'Bounced'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_email = models.EmailField()
    recipient_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='email_logs')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Related notification
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, null=True, blank=True, related_name='email_logs')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    # Error details
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
    
    def __str__(self):
        return f"Email to {self.recipient_email} - {self.get_status_display()}"


class UserNotificationPreferences(models.Model):
    """Model for user notification preferences"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_announcements = models.BooleanField(default=True)
    email_loan_updates = models.BooleanField(default=True)
    email_equipment_updates = models.BooleanField(default=True)
    email_payment_reminders = models.BooleanField(default=True)
    email_system_notifications = models.BooleanField(default=True)
    
    # SMS preferences
    sms_announcements = models.BooleanField(default=False)
    sms_loan_updates = models.BooleanField(default=True)
    sms_equipment_updates = models.BooleanField(default=False)
    sms_payment_reminders = models.BooleanField(default=True)
    sms_system_notifications = models.BooleanField(default=False)
    
    # Dashboard preferences
    dashboard_announcements = models.BooleanField(default=True)
    dashboard_notifications = models.BooleanField(default=True)
    
    # Frequency settings
    digest_frequency = models.CharField(
        max_length=15,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
            ('never', 'Never'),
        ],
        default='immediate'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Notification Preferences'
        verbose_name_plural = 'User Notification Preferences'
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Notification Preferences"
