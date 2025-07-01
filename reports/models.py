from django.db import models
from django.conf import settings
import uuid

class ReportCategory(models.Model):
    """Model for categorizing different types of reports"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon class name")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Report Category'
        verbose_name_plural = 'Report Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReportTemplate(models.Model):
    """Model for defining report templates"""
    
    REPORT_TYPES = [
        ('financial', 'Financial Report'),
        ('loans', 'Loans Report'),
        ('equipment', 'Equipment Report'),
        ('membership', 'Membership Report'),
        ('contributions', 'Contributions Report'),
        ('custom', 'Custom Report'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(ReportCategory, on_delete=models.CASCADE, related_name='templates')
    report_type = models.CharField(max_length=15, choices=REPORT_TYPES)
    
    # Template configuration
    sql_query = models.TextField(blank=True, null=True, help_text="SQL query for custom reports")
    fields_config = models.JSONField(default=dict, help_text="Configuration for report fields")
    filters_config = models.JSONField(default=dict, help_text="Available filters for the report")
    
    # Access control
    allowed_roles = models.JSONField(default=list, help_text="List of roles that can access this report")
    is_public = models.BooleanField(default=False)
    
    # Output settings
    default_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Report Template'
        verbose_name_plural = 'Report Templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class GeneratedReport(models.Model):
    """Model for tracking generated reports"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='generated_reports')
    title = models.CharField(max_length=200)
    
    # Generation parameters
    filters_applied = models.JSONField(default=dict, help_text="Filters applied when generating the report")
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    
    # Output details
    format = models.CharField(max_length=10, choices=ReportTemplate.FORMAT_CHOICES)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True, help_text="File size in bytes")
    
    # Status and timing
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    generated_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    
    # Analytics
    download_count = models.PositiveIntegerField(default=0)
    last_downloaded = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Generated Report'
        verbose_name_plural = 'Generated Reports'
        indexes = [
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['template', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    @property
    def is_available(self):
        from django.utils import timezone
        return (
            self.status == 'completed' and 
            (not self.expires_at or self.expires_at > timezone.now())
        )


class ScheduledReport(models.Model):
    """Model for scheduling automatic report generation"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('inactive', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='scheduled_reports')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Scheduling configuration
    frequency = models.CharField(max_length=15, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    
    # Time settings
    generation_time = models.TimeField(default='09:00:00')
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    
    # Recipients
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='scheduled_reports')
    email_recipients = models.TextField(blank=True, null=True, help_text="Additional email addresses (comma-separated)")
    
    # Output settings
    format = models.CharField(max_length=10, choices=ReportTemplate.FORMAT_CHOICES, default='pdf')
    
    # Status
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    
    # Execution tracking
    last_run = models.DateTimeField(blank=True, null=True)
    next_run = models.DateTimeField(blank=True, null=True)
    run_count = models.PositiveIntegerField(default=0)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_scheduled_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Scheduled Report'
        verbose_name_plural = 'Scheduled Reports'
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class Dashboard(models.Model):
    """Model for defining custom dashboards"""
    
    DASHBOARD_TYPES = [
        ('overview', 'Overview Dashboard'),
        ('financial', 'Financial Dashboard'),
        ('operations', 'Operations Dashboard'),
        ('analytics', 'Analytics Dashboard'),
        ('custom', 'Custom Dashboard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    dashboard_type = models.CharField(max_length=15, choices=DASHBOARD_TYPES)
    
    # Configuration
    layout_config = models.JSONField(default=dict, help_text="Dashboard layout configuration")
    widgets_config = models.JSONField(default=list, help_text="Dashboard widgets configuration")
    
    # Access control
    allowed_roles = models.JSONField(default=list, help_text="List of roles that can access this dashboard")
    is_default = models.BooleanField(default=False, help_text="Default dashboard for new users")
    is_public = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_dashboards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
    
    def __str__(self):
        return f"{self.name} ({self.get_dashboard_type_display()})"


class DashboardWidget(models.Model):
    """Model for individual dashboard widgets"""
    
    WIDGET_TYPES = [
        ('chart', 'Chart Widget'),
        ('metric', 'Metric Widget'),
        ('table', 'Table Widget'),
        ('list', 'List Widget'),
        ('calendar', 'Calendar Widget'),
        ('progress', 'Progress Widget'),
        ('custom', 'Custom Widget'),
    ]
    
    CHART_TYPES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
        ('area', 'Area Chart'),
        ('scatter', 'Scatter Plot'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    widget_type = models.CharField(max_length=15, choices=WIDGET_TYPES)
    chart_type = models.CharField(max_length=15, choices=CHART_TYPES, blank=True, null=True)
    
    # Data configuration
    data_source = models.CharField(max_length=200, help_text="Source of data for the widget")
    query_config = models.JSONField(default=dict, help_text="Query configuration for data retrieval")
    
    # Display configuration
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=4)
    height = models.PositiveIntegerField(default=3)
    
    display_config = models.JSONField(default=dict, help_text="Widget display configuration")
    refresh_interval = models.PositiveIntegerField(default=300, help_text="Refresh interval in seconds")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
        verbose_name = 'Dashboard Widget'
        verbose_name_plural = 'Dashboard Widgets'
    
    def __str__(self):
        return f"{self.name} - {self.get_widget_type_display()}"


class ReportAccess(models.Model):
    """Model for tracking report access and downloads"""
    
    ACTION_CHOICES = [
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('email', 'Emailed'),
        ('share', 'Shared'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(GeneratedReport, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='report_accesses')
    action = models.CharField(max_length=15, choices=ACTION_CHOICES)
    
    # Access details
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Report Access'
        verbose_name_plural = 'Report Accesses'
        indexes = [
            models.Index(fields=['report', 'action']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} {self.get_action_display()} {self.report.title}"


class AnalyticsMetric(models.Model):
    """Model for storing analytics metrics"""
    
    METRIC_TYPES = [
        ('counter', 'Counter'),
        ('gauge', 'Gauge'),
        ('histogram', 'Histogram'),
        ('summary', 'Summary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    metric_type = models.CharField(max_length=15, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=15, decimal_places=4)
    
    # Metadata
    tags = models.JSONField(default=dict, help_text="Metric tags/labels")
    description = models.TextField(blank=True, null=True)
    
    # Time series data
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Analytics Metric'
        verbose_name_plural = 'Analytics Metrics'
        indexes = [
            models.Index(fields=['name', 'date']),
            models.Index(fields=['metric_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value} ({self.date})"
