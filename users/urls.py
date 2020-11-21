from django.urls import path
from . import views
from django.contrib.auth import views as av

urlpatterns = [
    path('login/', av.LoginView.as_view(), name='login'),
    path('logout/', av.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name="Register"),
    path('edit/', views.edit_account, name="Edit Account"),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('change-password', av.PasswordChangeView.as_view(), name='change_password'),
    path('password-change/done', av.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('reset-password', av.PasswordResetView.as_view(), name='reset_password'),
    path('reset-password/done', av.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', av.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset-password/complete/', av.PasswordResetCompleteView.as_view(), name='password_reset_complete')
]