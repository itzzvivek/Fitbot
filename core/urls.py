from django.urls import path
from .views import check_attendance, view_subscription, whatsapp_check_in, whatsapp_subscription_status, handle_whatsapp_message, register_client

urlpatterns = [
    path('whatsapp/register/', register_client, name='register_client'),
    path('attendance/', check_attendance, name='check_attendance'),
    path('subscription/', view_subscription, name='view_subscription'),
    path('whatsapp_check_in/', whatsapp_check_in, name='whatsapp_check_in'),
    path('whatsapp/subscription-status/', whatsapp_subscription_status, name='whatsapp_subscription_status'),
    path('whatsapp/message/', handle_whatsapp_message, name='handle_whatsapp_message'),
]
