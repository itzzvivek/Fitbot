from django.urls import path
from .views import check_in, subscription_status, handle_whatsapp_message, register_client

urlpatterns = [
    path('whatsapp/register/', register_client, name='register_client'),
    path('whatsapp_check_in/', check_in, name='check_in'),
    path('whatsapp/my-plan/', subscription_status, name='subscription_status'),
    path('whatsapp/message/', handle_whatsapp_message, name='handle_whatsapp_message'),
]