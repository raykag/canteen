from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for the viewsets
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')

urlpatterns = [
    # Dashboard routes (for serving React app)
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    
    # API routes
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='api_login'),
    path('auth/logout/', views.LogoutView.as_view(), name='api_logout'),
    path('auth/profile/', views.ProfileView.as_view(), name='profile'),
]