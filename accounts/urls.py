from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('verify/', views.UserVerifyCodeView.as_view(), name='verify_code'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('logout/', views.UserLogoutView.as_view(), name='user_logout'),
    path('forget/', views.UserForgetPasswordView.as_view(), name='user_forget'),
    path('verifypass/',views.UserVerifyResetPasswordView.as_view(),name='password_verify'),
    path('verifypass/done/',views.UserVerifyResetPasswordDoneView.as_view(),name='password_done'),
]
