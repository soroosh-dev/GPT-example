"""
URL configuration for gaply project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from account.views import register, pay_subscription, success, cancel, stripe_webhook
from gpt.views import single_prompt, chat_history

GLOBAL_PREFIX='gaply_challenge/'

urlpatterns = [
    path(GLOBAL_PREFIX+'admin/', admin.site.urls),
    path(GLOBAL_PREFIX+'api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(GLOBAL_PREFIX+'api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(GLOBAL_PREFIX+'api/v1/auth/register/', register, name="register"),
    path(GLOBAL_PREFIX+'api/v1/success/', success, name='payment_success'),
    path(GLOBAL_PREFIX+'api/v1/cancel/', cancel, name='payment_failed'),
    path(GLOBAL_PREFIX+'api/v1/webhook/', stripe_webhook, name='webhook'),
    path(GLOBAL_PREFIX+'api/v1/chat/', single_prompt, name='prompt'),
    path(GLOBAL_PREFIX+'api/v1/subscribe/',pay_subscription, name='subscribe'),
    path(GLOBAL_PREFIX+'api/v1/chat/history/', chat_history, name="chat_history"),
]
