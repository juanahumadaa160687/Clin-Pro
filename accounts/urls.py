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
    path('password/', PasswordsChangeView.as_view(), name='change_password'),
    path('password_reset/', PasswordsResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', PasswordsResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_change_done.html'), name='password_reset_complete'),
    path('activate_mfa/', activate_mfa, name='activate_mfa'),
    path('verify_mfa/', verify_mfa, name='verify_mfa'),
    path('deactivate_mfa/', deactivate_mfa, name='deactivate_mfa'),
]