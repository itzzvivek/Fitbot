from django.urls import path
from .views import check_in, subscription_status, handle_whatsapp_message, register_client, notify_expiring_subscriptions

urlpatterns = [
    path('register/', register_client, name='register_client'),
    path('check_in/', check_in, name='check_in'),
    path('my-plan/', subscription_status, name='subscription_status'),
    path('notify-expiring-subscription/', notify_expiring_subscriptions, name='notify_expiring_subscriptions'),
    path('handle-whatsapp-message/', handle_whatsapp_message, name='handle_whatsapp_message'),
]