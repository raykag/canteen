from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class Contribution(models.Model):
    """Model for tracking member contributions"""
    
    CONTRIBUTION_TYPES = [
        ('monthly', 'Monthly Contribution'),
        ('special', 'Special Contribution'),
        ('share', 'Share Capital'),
        ('registration', 'Registration Fee'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contributions')
    type = models.CharField(max_length=15, choices=CONTRIBUTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date_contributed = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='cash')
    receipt_number = models.CharField(max_length=50, unique=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_contributions')
    
    class Meta:
        ordering = ['-date_contributed']
        verbose_name = 'Contribution'
        verbose_name_plural = 'Contributions'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.get_type_display()} - KES {self.amount}"


class Loan(models.Model):
    """Model for tracking loans issued to members"""
    
    LOAN_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('rejected', 'Rejected'),
    ]
    
    LOAN_TYPES = [
        ('agricultural', 'Agricultural Loan'),
        ('emergency', 'Emergency Loan'),
        ('business', 'Business Development Loan'),
        ('education', 'Education Loan'),
        ('housing', 'Housing Loan'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=15, choices=LOAN_TYPES)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual interest rate as percentage")
    loan_period_months = models.PositiveIntegerField(help_text="Loan period in months")
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Loan lifecycle dates
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(blank=True, null=True)
    disbursement_date = models.DateTimeField(blank=True, null=True)
    expected_completion_date = models.DateField(blank=True, null=True)
    
    status = models.CharField(max_length=15, choices=LOAN_STATUS, default='pending')
    purpose = models.TextField(help_text="Purpose of the loan")
    collateral = models.TextField(blank=True, null=True, help_text="Description of collateral")
    
    # Staff handling
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans')
    disbursed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='disbursed_loans')
    
    # Financial tracking
    total_amount_due = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_remaining = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-application_date']
        verbose_name = 'Loan'
        verbose_name_plural = 'Loans'
    
    def __str__(self):
        return f"{self.borrower.get_full_name()} - {self.get_loan_type_display()} - KES {self.principal_amount}"
    
    def save(self, *args, **kwargs):
        if self.interest_rate and self.principal_amount and self.loan_period_months:
            # Simple interest calculation
            monthly_interest_rate = self.interest_rate / 100 / 12
            if monthly_interest_rate > 0:
                self.monthly_payment = (
                    self.principal_amount * monthly_interest_rate * 
                    (1 + monthly_interest_rate) ** self.loan_period_months
                ) / ((1 + monthly_interest_rate) ** self.loan_period_months - 1)
            else:
                self.monthly_payment = self.principal_amount / self.loan_period_months
            
            self.total_amount_due = self.monthly_payment * self.loan_period_months
            self.balance_remaining = self.total_amount_due - self.amount_paid
        
        super().save(*args, **kwargs)


class LoanRepayment(models.Model):
    """Model for tracking loan repayments"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, default='cash')
    receipt_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_repayments')
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Loan Repayment'
        verbose_name_plural = 'Loan Repayments'
    
    def __str__(self):
        return f"{self.loan.borrower.get_full_name()} - KES {self.amount} - {self.payment_date.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update loan amount_paid and balance_remaining
        self.loan.amount_paid = sum(self.loan.repayments.values_list('amount', flat=True))
        self.loan.balance_remaining = self.loan.total_amount_due - self.loan.amount_paid
        
        # Check if loan is completed
        if self.loan.balance_remaining <= 0 and self.loan.status == 'active':
            self.loan.status = 'completed'
        
        self.loan.save()


class FinancialAccount(models.Model):
    """Model for tracking cooperative's financial accounts"""
    
    ACCOUNT_TYPES = [
        ('cash', 'Cash Account'),
        ('bank', 'Bank Account'),
        ('shares', 'Shares Account'),
        ('loans', 'Loans Account'),
        ('reserves', 'Reserves Account'),
    ]
    
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Financial Account'
        verbose_name_plural = 'Financial Accounts'
    
    def __str__(self):
        return f"{self.name} - KES {self.current_balance}"


class Transaction(models.Model):
    """Model for recording all financial transactions"""
    
    TRANSACTION_TYPES = [
        ('contribution', 'Member Contribution'),
        ('loan_disbursement', 'Loan Disbursement'),
        ('loan_repayment', 'Loan Repayment'),
        ('expense', 'Expense'),
        ('income', 'Other Income'),
        ('transfer', 'Account Transfer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    reference_number = models.CharField(max_length=50, unique=True)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_transactions')
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    # Links to related objects
    contribution = models.ForeignKey(Contribution, on_delete=models.SET_NULL, null=True, blank=True)
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True)
    repayment = models.ForeignKey(LoanRepayment, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - KES {self.amount} - {self.transaction_date.strftime('%Y-%m-%d')}"
