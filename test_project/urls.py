"""test_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('sign-up/username/', views.sign_up_username, name='sign-up-username'),
    path('sign-up/email/', views.sign_up_email, name='sign-up-email'),
    path('sign-up/phone/', views.sign_up_phone, name='sign-up-phone'),
    path('sign-in/', views.sign_in, name='sign-in'),
    path('sign-out/', views.sign_out, name='sign-out'),
    path('account/', views.account, name='account'),
    path('account/user/', views.user, name='user'),
    path('account/password/', views.password, name='user-password'),
    path('account/user/verify/<slug:token_type>/<int:token_id>/', views.verify_user, name='verify-user'),
    path('account/user/verify/<slug:token_type>/<int:token_id>/<str:password>/', views.verify_user),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('forgot-password/verify/<slug:token_type>/<int:token_id>/', views.forgot_password_verify, name='forgot-password-verify'),
    path('forgot-password/verify/<slug:token_type>/<int:token_id>/<str:password>/', views.forgot_password_verify),
    path('forgot-password/password-reset/<int:pk>/', views.password_reset, name='password-reset'),

    path('account/', include('django_flex_user.urls')),
    path('admin/', admin.site.urls),
    # social-auth-app-django
    path('', include('social_django.urls', namespace='social')),
    # Django authentication views
    path('', include('django.contrib.auth.urls')),
]

urlpatterns += [
    # djangorestframework
    path('api-auth/', include('rest_framework.urls')),
]
