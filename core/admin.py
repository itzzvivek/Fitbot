from django.contrib import admin
from .models import Client, Attendance, Subscription


admin.site.register(Client)
admin.site.register(Attendance)
admin.site.register(Subscription)
