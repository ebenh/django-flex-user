from django.urls import path, include

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('csrf-tokens/', views.get_csrf_token),
    path('users/', views.FlexUsers.as_view()),
    path('users/user/', views.FlexUser.as_view()),
    path('users/user/oauth-providers/', views.OAuthProviders.as_view()),
    path('sessions/', views.Sessions.as_view()),

    path('otp-tokens/', views.OTPTokens.as_view()),
    path('otp-tokens/email/<str:pk>', views.EmailToken.as_view(), name='email-token'),
    path('otp-tokens/phone/<str:pk>', views.PhoneToken.as_view(), name='phone-token'),
]

# djangorestframework
urlpatterns = format_suffix_patterns(urlpatterns)
