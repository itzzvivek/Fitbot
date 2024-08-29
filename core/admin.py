from django.contrib import admin
from .models import GymOwner, Client, Attendance, Subscription


admin.site.register(GymOwner)
admin.site.register(Client)
admin.site.register(Attendance)
admin.site.register(Subscription)
