from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/<int:id>', profile, name='profile'),
    path('profile/<int:id>/edit', edit_profile, name='edit_profile'),
    path('profile/<int:id>/delete', delete_profile, name='delete_profile'),
    path('password/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
    path('activate_mfa/', activate_mfa, name='activate_mfa'),
    path('verify_mfa/', verify_mfa, name='verify_mfa'),
    path('deactivate_mfa/', deactivate_mfa, name='deactivate_mfa'),
]