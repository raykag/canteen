from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.db.models import Sum, Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserListSerializer, UserCreateSerializer,
    LoginSerializer, PasswordChangeSerializer, UserProfileSerializer,
    UserStatsSerializer
)
from .permissions import IsOwnerOrAdminOrStaff

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active_member', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['username', 'first_name', 'last_name', 'membership_date']
    ordering = ['first_name', 'last_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Only admins and staff can create users
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrStaff]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # Users can view/edit their own profile, admins/staff can edit anyone
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrStaff]
        else:
            # List and destroy require admin/staff permissions
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrStaff]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_staff_member:
            return User.objects.all()
        else:
            # Farmers can only see their own profile
            return User.objects.filter(id=user.id)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get user statistics"""
        user = self.get_object()
        
        # Only allow users to see their own stats, or admins/staff to see anyone's
        if not (request.user == user or request.user.is_admin or request.user.is_staff_member):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        from financial.models import Contribution, Loan
        from equipment.models import EquipmentAllocation
        from notifications.models import Notification
        
        stats = {
            'total_contributions': user.contributions.aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'total_loans': user.loans.aggregate(
                total=Sum('principal_amount')
            )['total'] or 0,
            'active_loans': user.loans.filter(
                status__in=['active', 'disbursed']
            ).count(),
            'equipment_allocations': user.equipment_allocations.filter(
                status='active'
            ).count(),
            'notifications_unread': user.notifications.filter(
                status__in=['pending', 'sent', 'delivered']
            ).count(),
        }
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password"""
        user = self.get_object()
        
        # Only allow users to change their own password, or admins to change anyone's
        if not (request.user == user or request.user.is_admin):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle user active status (admin only)"""
        if not request.user.is_admin:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'is_active': user.is_active
        })

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrStaff]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_staff_member:
            return UserProfile.objects.all()
        else:
            return UserProfile.objects.filter(user=user)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'})
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user's profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update current user's profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Dashboard views for serving React app
def dashboard_view(request):
    """Main dashboard view"""
    return render(request, 'dashboard.html')

def login_view(request):
    """Login page view"""
    return render(request, 'login.html')
