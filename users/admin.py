from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'role',
        'is_active_member', 'phone_number', 'membership_date', 'is_active'
    ]
    list_filter = ['role', 'is_active', 'is_active_member', 'membership_date']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'national_id']
    ordering = ['first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Cooperative Information', {
            'fields': (
                'role', 'phone_number', 'address', 'date_of_birth', 'national_id',
                'is_active_member', 'profile_picture'
            )
        }),
        ('Farmer Details', {
            'fields': ('farm_size', 'crops'),
            'classes': ('collapse',)
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Cooperative Information', {
            'fields': (
                'role', 'email', 'first_name', 'last_name', 'phone_number'
            )
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Staff can only see farmers
        return qs.filter(role='farmer')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'birth_date', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('User', {
            'fields': ['user']
        }),
        ('Profile Information', {
            'fields': ['bio', 'location', 'birth_date', 'avatar']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
