#!/usr/bin/env python
"""
Data seeding script for Farmers Cooperative Management System
Run this script to populate the database with sample data for demonstration
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmers_cooperative.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import UserProfile
from financial.models import Contribution, Loan, LoanRepayment, FinancialAccount, Transaction
from equipment.models import EquipmentCategory, Equipment, EquipmentAllocation
from notifications.models import NotificationCategory, Announcement
from reports.models import ReportCategory

User = get_user_model()

def create_users():
    """Create sample users with different roles"""
    print("Creating users...")
    
    # Create admin user
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@ngara-farmers.co.ke',
            'first_name': 'John',
            'last_name': 'Kimani',
            'role': 'admin',
            'phone_number': '+254722000001',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        UserProfile.objects.create(user=admin, bio="System Administrator")
        print(f"Created admin user: {admin.username}")
    
    # Create staff users
    staff_data = [
        {
            'username': 'staff1',
            'email': 'staff1@ngara-farmers.co.ke',
            'first_name': 'Mary',
            'last_name': 'Wanjiku',
            'phone_number': '+254722000002',
        },
        {
            'username': 'staff2',
            'email': 'staff2@ngara-farmers.co.ke',
            'first_name': 'Peter',
            'last_name': 'Mwangi',
            'phone_number': '+254722000003',
        }
    ]
    
    for data in staff_data:
        staff, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                **data,
                'role': 'staff',
                'is_staff': True,
            }
        )
        if created:
            staff.set_password('staff123')
            staff.save()
            UserProfile.objects.create(user=staff, bio="Cooperative Staff Member")
            print(f"Created staff user: {staff.username}")
    
    # Create farmer users
    farmers_data = [
        {
            'username': 'farmer1',
            'email': 'farmer1@example.com',
            'first_name': 'James',
            'last_name': 'Kariuki',
            'phone_number': '+254722000004',
            'address': 'Ngara, Nakuru County',
            'farm_size': Decimal('5.5'),
            'crops': 'Maize, Beans, Potatoes',
            'national_id': '12345678',
        },
        {
            'username': 'farmer2',
            'email': 'farmer2@example.com',
            'first_name': 'Grace',
            'last_name': 'Njeri',
            'phone_number': '+254722000005',
            'address': 'Ngara, Nakuru County',
            'farm_size': Decimal('3.2'),
            'crops': 'Vegetables, Maize',
            'national_id': '87654321',
        },
        {
            'username': 'farmer3',
            'email': 'farmer3@example.com',
            'first_name': 'Samuel',
            'last_name': 'Kiprotich',
            'phone_number': '+254722000006',
            'address': 'Ngara, Nakuru County',
            'farm_size': Decimal('8.0'),
            'crops': 'Maize, Wheat, Barley',
            'national_id': '11223344',
        },
        {
            'username': 'farmer4',
            'email': 'farmer4@example.com',
            'first_name': 'Ruth',
            'last_name': 'Wanjiru',
            'phone_number': '+254722000007',
            'address': 'Ngara, Nakuru County',
            'farm_size': Decimal('4.7'),
            'crops': 'Tomatoes, Onions, Cabbages',
            'national_id': '99887766',
        },
        {
            'username': 'farmer5',
            'email': 'farmer5@example.com',
            'first_name': 'David',
            'last_name': 'Kipkoech',
            'phone_number': '+254722000008',
            'address': 'Ngara, Nakuru County',
            'farm_size': Decimal('6.3'),
            'crops': 'Maize, Beans, Sunflower',
            'national_id': '55443322',
        }
    ]
    
    for data in farmers_data:
        farmer, created = User.objects.get_or_create(
            username=data['username'],
            defaults={**data, 'role': 'farmer'}
        )
        if created:
            farmer.set_password('farmer123')
            farmer.save()
            UserProfile.objects.create(user=farmer, bio=f"Farmer from {data['address']}")
            print(f"Created farmer user: {farmer.username}")

def create_financial_accounts():
    """Create financial accounts"""
    print("Creating financial accounts...")
    
    accounts_data = [
        {
            'name': 'Main Cash Account',
            'account_type': 'cash',
            'current_balance': Decimal('150000.00'),
            'description': 'Main cash account for daily operations'
        },
        {
            'name': 'KCB Bank Account',
            'account_type': 'bank',
            'account_number': '1234567890',
            'bank_name': 'Kenya Commercial Bank',
            'current_balance': Decimal('850000.00'),
            'description': 'Main bank account'
        },
        {
            'name': 'Member Shares Account',
            'account_type': 'shares',
            'current_balance': Decimal('500000.00'),
            'description': 'Member share capital'
        },
        {
            'name': 'Loans Account',
            'account_type': 'loans',
            'current_balance': Decimal('300000.00'),
            'description': 'Outstanding loans account'
        }
    ]
    
    for data in accounts_data:
        account, created = FinancialAccount.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"Created account: {account.name}")

def create_contributions():
    """Create sample contributions"""
    print("Creating contributions...")
    
    farmers = User.objects.filter(role='farmer')
    staff = User.objects.filter(role='staff').first()
    
    contribution_types = ['monthly', 'special', 'share', 'registration']
    
    for i, farmer in enumerate(farmers):
        # Create registration fee
        Contribution.objects.get_or_create(
            member=farmer,
            type='registration',
            defaults={
                'amount': Decimal('1000.00'),
                'description': 'Membership registration fee',
                'payment_method': 'cash',
                'receipt_number': f'REG-{farmer.id:04d}',
                'recorded_by': staff
            }
        )
        
        # Create monthly contributions for the last 6 months
        for month in range(6):
            date_offset = datetime.now() - timedelta(days=30 * month)
            amount = Decimal('500.00') + Decimal(str(i * 50))  # Varying amounts
            
            Contribution.objects.get_or_create(
                member=farmer,
                type='monthly',
                date_contributed=date_offset,
                defaults={
                    'amount': amount,
                    'description': f'Monthly contribution for {date_offset.strftime("%B %Y")}',
                    'payment_method': 'bank_transfer' if i % 2 else 'cash',
                    'receipt_number': f'MONTH-{farmer.id:04d}-{month:02d}',
                    'recorded_by': staff
                }
            )
        
        print(f"Created contributions for farmer: {farmer.username}")

def create_equipment():
    """Create equipment categories and equipment"""
    print("Creating equipment...")
    
    # Create equipment categories
    categories_data = [
        {'name': 'Tractors', 'description': 'Farm tractors and attachments'},
        {'name': 'Ploughs', 'description': 'Ploughing equipment'},
        {'name': 'Harvesters', 'description': 'Harvesting equipment'},
        {'name': 'Irrigation', 'description': 'Irrigation systems and pumps'},
        {'name': 'Tools', 'description': 'Hand tools and implements'},
    ]
    
    for data in categories_data:
        category, created = EquipmentCategory.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"Created equipment category: {category.name}")
    
    # Create equipment items
    admin = User.objects.filter(role='admin').first()
    tractor_category = EquipmentCategory.objects.get(name='Tractors')
    plough_category = EquipmentCategory.objects.get(name='Ploughs')
    
    equipment_data = [
        {
            'name': 'Massey Ferguson 240 Tractor',
            'category': tractor_category,
            'description': ' 50HP tractor suitable for medium-scale farming',
            'brand': 'Massey Ferguson',
            'model': 'MF 240',
            'serial_number': 'MF240001',
            'purchase_date': date(2023, 1, 15),
            'purchase_price': Decimal('850000.00'),
            'supplier': 'Massey Ferguson Kenya',
            'storage_location': 'Main Equipment Shed'
        },
        {
            'name': 'John Deere 5055E Tractor',
            'category': tractor_category,
            'description': '55HP utility tractor',
            'brand': 'John Deere',
            'model': '5055E',
            'serial_number': 'JD5055001',
            'purchase_date': date(2023, 3, 20),
            'purchase_price': Decimal('950000.00'),
            'supplier': 'John Deere Kenya',
            'storage_location': 'Main Equipment Shed'
        },
        {
            'name': '3-Disc Plough',
            'category': plough_category,
            'description': 'Heavy-duty 3-disc plough for tractors',
            'brand': 'Baldan',
            'model': 'AFTD-3',
            'serial_number': 'BLD3001',
            'purchase_date': date(2023, 2, 10),
            'purchase_price': Decimal('45000.00'),
            'supplier': 'Farm Equipment Kenya',
            'storage_location': 'Equipment Store'
        },
        {
            'name': '4-Disc Plough',
            'category': plough_category,
            'description': 'Heavy-duty 4-disc plough for large tractors',
            'brand': 'Baldan',
            'model': 'AFTD-4',
            'serial_number': 'BLD4001',
            'purchase_date': date(2023, 4, 5),
            'purchase_price': Decimal('55000.00'),
            'supplier': 'Farm Equipment Kenya',
            'storage_location': 'Equipment Store'
        }
    ]
    
    for data in equipment_data:
        equipment, created = Equipment.objects.get_or_create(
            serial_number=data['serial_number'],
            defaults={**data, 'created_by': admin}
        )
        if created:
            print(f"Created equipment: {equipment.name}")

def create_loans():
    """Create sample loans"""
    print("Creating loans...")
    
    farmers = User.objects.filter(role='farmer')[:3]  # First 3 farmers
    staff = User.objects.filter(role='staff').first()
    admin = User.objects.filter(role='admin').first()
    
    loans_data = [
        {
            'borrower': farmers[0],
            'loan_type': 'agricultural',
            'principal_amount': Decimal('50000.00'),
            'interest_rate': Decimal('12.00'),
            'loan_period_months': 12,
            'purpose': 'Purchase of seeds and fertilizers for maize farming',
            'status': 'active',
            'approved_by': admin,
            'disbursed_by': staff,
            'approval_date': datetime.now() - timedelta(days=30),
            'disbursement_date': datetime.now() - timedelta(days=25),
        },
        {
            'borrower': farmers[1],
            'loan_type': 'emergency',
            'principal_amount': Decimal('25000.00'),
            'interest_rate': Decimal('10.00'),
            'loan_period_months': 6,
            'purpose': 'Medical emergency funds',
            'status': 'active',
            'approved_by': admin,
            'disbursed_by': staff,
            'approval_date': datetime.now() - timedelta(days=60),
            'disbursement_date': datetime.now() - timedelta(days=55),
        },
        {
            'borrower': farmers[2],
            'loan_type': 'business',
            'principal_amount': Decimal('100000.00'),
            'interest_rate': Decimal('15.00'),
            'loan_period_months': 24,
            'purpose': 'Expand vegetable farming business',
            'status': 'pending',
        }
    ]
    
    for data in loans_data:
        loan, created = Loan.objects.get_or_create(
            borrower=data['borrower'],
            principal_amount=data['principal_amount'],
            defaults=data
        )
        if created:
            print(f"Created loan for: {loan.borrower.username}")
            
            # Create some repayments for active loans
            if loan.status == 'active':
                repayment_amount = loan.monthly_payment
                LoanRepayment.objects.get_or_create(
                    loan=loan,
                    amount=repayment_amount,
                    defaults={
                        'payment_method': 'bank_transfer',
                        'receipt_number': f'REP-{loan.id}-001',
                        'notes': 'Monthly loan repayment',
                        'recorded_by': staff
                    }
                )

def create_notifications():
    """Create notification categories and announcements"""
    print("Creating notifications...")
    
    # Create notification categories
    categories_data = [
        {
            'name': 'General Announcements',
            'description': 'General cooperative announcements',
            'color_code': '#007bff',
            'icon': 'fas fa-bullhorn'
        },
        {
            'name': 'Financial Updates',
            'description': 'Financial and payment related notifications',
            'color_code': '#28a745',
            'icon': 'fas fa-coins'
        },
        {
            'name': 'Equipment Notices',
            'description': 'Equipment allocation and maintenance notices',
            'color_code': '#ffc107',
            'icon': 'fas fa-tools'
        },
        {
            'name': 'System Alerts',
            'description': 'System maintenance and technical alerts',
            'color_code': '#dc3545',
            'icon': 'fas fa-exclamation-triangle'
        }
    ]
    
    for data in categories_data:
        category, created = NotificationCategory.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"Created notification category: {category.name}")
    
    # Create sample announcements
    admin = User.objects.filter(role='admin').first()
    general_category = NotificationCategory.objects.get(name='General Announcements')
    
    announcements_data = [
        {
            'title': 'Welcome to Ngara Farmers Cooperative',
            'content': 'Welcome to our new digital platform! This system will help us manage our cooperative activities more efficiently. You can now view your contributions, apply for loans, request equipment, and stay updated with announcements.',
            'category': general_category,
            'target_audience': 'all',
            'priority': 'high',
            'status': 'published',
            'show_on_dashboard': True,
            'created_by': admin,
            'published_at': datetime.now()
        },
        {
            'title': 'Monthly Meeting - January 2024',
            'content': 'Our monthly cooperative meeting is scheduled for January 30th, 2024 at 2:00 PM at the Ngara Community Center. Agenda items include financial reports, new equipment purchases, and planning for the upcoming planting season.',
            'category': general_category,
            'target_audience': 'all',
            'priority': 'normal',
            'status': 'published',
            'show_on_dashboard': True,
            'created_by': admin,
            'published_at': datetime.now() - timedelta(days=5)
        }
    ]
    
    for data in announcements_data:
        announcement, created = Announcement.objects.get_or_create(
            title=data['title'],
            defaults=data
        )
        if created:
            print(f"Created announcement: {announcement.title}")

def create_report_categories():
    """Create report categories"""
    print("Creating report categories...")
    
    categories_data = [
        {
            'name': 'Financial Reports',
            'description': 'Financial statements, contributions, and loan reports',
            'icon': 'fas fa-chart-line'
        },
        {
            'name': 'Member Reports',
            'description': 'Membership and user activity reports',
            'icon': 'fas fa-users'
        },
        {
            'name': 'Equipment Reports',
            'description': 'Equipment utilization and maintenance reports',
            'icon': 'fas fa-tools'
        },
        {
            'name': 'Custom Reports',
            'description': 'Custom and ad-hoc reports',
            'icon': 'fas fa-file-alt'
        }
    ]
    
    for data in categories_data:
        category, created = ReportCategory.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"Created report category: {category.name}")

def main():
    """Main function to run all seeding operations"""
    print("🌱 Starting data seeding for Farmers Cooperative Management System...")
    print("=" * 60)
    
    try:
        create_users()
        print()
        
        create_financial_accounts()
        print()
        
        create_contributions()
        print()
        
        create_equipment()
        print()
        
        create_loans()
        print()
        
        create_notifications()
        print()
        
        create_report_categories()
        print()
        
        print("=" * 60)
        print("✅ Data seeding completed successfully!")
        print()
        print("Sample login credentials:")
        print("Admin: username='admin', password='admin123'")
        print("Staff: username='staff1', password='staff123'")
        print("Farmer: username='farmer1', password='farmer123'")
        print()
        print("You can now run the server with: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error during data seeding: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()