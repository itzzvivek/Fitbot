from django.urls import path
from .views import check_attendance, view_subscription, whatsapp_check_in

urlpatterns = [
    path('attendance/', check_attendance, name='check_attendance'),
    path('subscription/', view_subscription, name='view_subscription'),
    path('whatsapp_check_in/', whatsapp_check_in, name='whatsapp_check_in'),
]
