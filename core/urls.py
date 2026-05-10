from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('contact/messages/', views.contact_messages, name='contact_messages'),
    
    path('auth/login/', auth_views.LoginView.as_view(template_name='core/auth/login.html'), name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    path('auth/register/', views.register, name='register'),
    
    path('auth/password-reset/', auth_views.PasswordResetView.as_view(
        template_name='core/auth/password_reset.html',
        email_template_name='core/auth/password_reset_email.html',
        subject_template_name='core/auth/password_reset_subject.txt'
    ), name='password_reset'),
    
    path('auth/password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/auth/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('auth/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    
    path('auth/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/auth/password_reset_complete.html'
    ), name='password_reset_complete'),
]
