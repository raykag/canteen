from rest_framework import serializers
from .models import Contribution, Loan, LoanRepayment, FinancialAccount, Transaction
from users.serializers import UserListSerializer

class ContributionSerializer(serializers.ModelSerializer):
    member = UserListSerializer(read_only=True)
    recorded_by = UserListSerializer(read_only=True)
    
    class Meta:
        model = Contribution
        fields = '__all__'
        read_only_fields = ['id', 'date_contributed', 'recorded_by']

class LoanSerializer(serializers.ModelSerializer):
    borrower = UserListSerializer(read_only=True)
    approved_by = UserListSerializer(read_only=True)
    disbursed_by = UserListSerializer(read_only=True)
    
    class Meta:
        model = Loan
        fields = '__all__'
        read_only_fields = [
            'id', 'application_date', 'monthly_payment', 'total_amount_due',
            'amount_paid', 'balance_remaining', 'approved_by', 'disbursed_by'
        ]

class LoanRepaymentSerializer(serializers.ModelSerializer):
    loan = LoanSerializer(read_only=True)
    recorded_by = UserListSerializer(read_only=True)
    
    class Meta:
        model = LoanRepayment
        fields = '__all__'
        read_only_fields = ['id', 'payment_date', 'recorded_by']

class FinancialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialAccount
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    member = UserListSerializer(read_only=True)
    recorded_by = UserListSerializer(read_only=True)
    account = FinancialAccountSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'transaction_date', 'recorded_by']