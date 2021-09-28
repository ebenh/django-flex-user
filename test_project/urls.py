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
    path('accounts/password-reset/find-my-account/', views.search_otp_tokens),
    path('accounts/password-reset/verify/<slug:token_type>/<int:token_id>/', views.verify_otp),

    path('accounts/', include('django_flex_user.urls')),
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
