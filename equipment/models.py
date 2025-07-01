from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid

class EquipmentCategory(models.Model):
    """Model for categorizing equipment types"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Equipment Category'
        verbose_name_plural = 'Equipment Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Equipment(models.Model):
    """Model for tracking agricultural equipment owned by the cooperative"""
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('out_of_service', 'Out of Service'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
        ('damaged', 'Damaged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE, related_name='equipment')
    description = models.TextField()
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Purchase information
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    supplier = models.CharField(max_length=200, blank=True, null=True)
    
    # Current status
    condition = models.CharField(max_length=15, choices=CONDITION_CHOICES, default='excellent')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    current_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Location and storage
    storage_location = models.CharField(max_length=200, blank=True, null=True)
    
    # Maintenance
    last_maintenance_date = models.DateField(blank=True, null=True)
    next_maintenance_date = models.DateField(blank=True, null=True)
    maintenance_cost_ytd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Images and documents
    image = models.ImageField(upload_to='equipment_images/', blank=True, null=True)
    manual_document = models.FileField(upload_to='equipment_manuals/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_equipment')
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    @property
    def total_allocations(self):
        return self.allocations.count()
    
    @property
    def current_allocation(self):
        return self.allocations.filter(status='active').first()


class EquipmentAllocation(models.Model):
    """Model for tracking equipment allocations to farmers"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('active', 'Active/In Use'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('damaged', 'Returned Damaged'),
        ('cancelled', 'Cancelled'),
    ]
    
    ALLOCATION_TYPES = [
        ('individual', 'Individual Allocation'),
        ('group', 'Group Allocation'),
        ('seasonal', 'Seasonal Allocation'),
        ('emergency', 'Emergency Allocation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='allocations')
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipment_allocations')
    allocation_type = models.CharField(max_length=15, choices=ALLOCATION_TYPES, default='individual')
    
    # Allocation period
    requested_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    purpose = models.TextField(help_text="Purpose for requesting the equipment")
    
    # Financial aspects
    rental_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Daily/weekly rental fee")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_paid = models.BooleanField(default=False)
    
    # Condition tracking
    condition_at_allocation = models.CharField(max_length=15, choices=Equipment.CONDITION_CHOICES)
    condition_at_return = models.CharField(max_length=15, choices=Equipment.CONDITION_CHOICES, blank=True, null=True)
    damage_notes = models.TextField(blank=True, null=True)
    damage_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Staff handling
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_allocations')
    allocated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_allocations')
    returned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_returns')
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-requested_date']
        verbose_name = 'Equipment Allocation'
        verbose_name_plural = 'Equipment Allocations'
    
    def __str__(self):
        return f"{self.equipment.name} → {self.farmer.get_full_name()} ({self.get_status_display()})"
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return (
            self.status == 'active' and 
            self.expected_return_date < timezone.now().date()
        )
    
    @property
    def days_allocated(self):
        from django.utils import timezone
        if self.actual_return_date:
            return (self.actual_return_date - self.start_date).days
        elif self.status == 'active':
            return (timezone.now().date() - self.start_date).days
        return 0
    
    def save(self, *args, **kwargs):
        # Update equipment status based on allocation status
        if self.status == 'active' and self.equipment.status != 'in_use':
            self.equipment.status = 'in_use'
            self.equipment.save()
        elif self.status == 'returned' and self.equipment.status == 'in_use':
            # Check if there are other active allocations
            other_active = EquipmentAllocation.objects.filter(
                equipment=self.equipment,
                status='active'
            ).exclude(id=self.id).exists()
            
            if not other_active:
                self.equipment.status = 'available'
                self.equipment.save()
        
        super().save(*args, **kwargs)


class MaintenanceRecord(models.Model):
    """Model for tracking equipment maintenance"""
    
    MAINTENANCE_TYPES = [
        ('routine', 'Routine Maintenance'),
        ('repair', 'Repair'),
        ('service', 'Service'),
        ('inspection', 'Inspection'),
        ('emergency', 'Emergency Repair'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=15, choices=MAINTENANCE_TYPES)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Dates
    scheduled_date = models.DateField(blank=True, null=True)
    start_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)
    
    # Service provider
    service_provider = models.CharField(max_length=200, blank=True, null=True)
    technician_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Parts and materials
    parts_used = models.TextField(blank=True, null=True, help_text="List of parts and materials used")
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Documentation
    receipt_image = models.ImageField(upload_to='maintenance_receipts/', blank=True, null=True)
    before_image = models.ImageField(upload_to='maintenance_before/', blank=True, null=True)
    after_image = models.ImageField(upload_to='maintenance_after/', blank=True, null=True)
    
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_maintenance')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Maintenance Record'
        verbose_name_plural = 'Maintenance Records'
    
    def __str__(self):
        return f"{self.equipment.name} - {self.get_maintenance_type_display()} - {self.start_date}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update equipment's last maintenance date and YTD cost
        self.equipment.last_maintenance_date = self.start_date
        self.equipment.maintenance_cost_ytd += self.cost
        self.equipment.save()


class EquipmentRequest(models.Model):
    """Model for farmers to request new equipment or suggest purchases"""
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('purchased', 'Purchased'),
        ('rejected', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipment_requests')
    equipment_name = models.CharField(max_length=200)
    category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE, related_name='requests')
    description = models.TextField()
    justification = models.TextField(help_text="Why this equipment is needed")
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted')
    
    # Supporting documents
    supporting_document = models.FileField(upload_to='equipment_requests/', blank=True, null=True)
    
    # Review and decision
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    review_date = models.DateTimeField(blank=True, null=True)
    review_notes = models.TextField(blank=True, null=True)
    
    # If approved and purchased
    purchased_equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Equipment Request'
        verbose_name_plural = 'Equipment Requests'
    
    def __str__(self):
        return f"{self.equipment_name} requested by {self.requested_by.get_full_name()}"
