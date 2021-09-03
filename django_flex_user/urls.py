from django.urls import path, include

from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('csrf-tokens/', views.get_csrf_token),
    path('users/', views.FlexUsers.as_view()),
    path('users/user/', views.FlexUser.as_view()),
    path('users/user/oauth-providers/', views.OAuthProviders.as_view()),
    path('sessions/', views.Sessions.as_view()),

    path('otp-devices/', views.OTPDevices.as_view()),
    path('otp-devices/<str:pk>', views.OTPDevice.as_view()),

    path('', include('social_django.urls', namespace='social')),
    # Password Reset
    path('', include('django.contrib.auth.urls')),
    # path('password_reset', include('django_rest_passwordreset.urls', namespace='password_reset')),
]

urlpatterns = format_suffix_patterns(urlpatterns)
