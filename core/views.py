from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from  .models import Client, Attendance, Subscription
from .utils import send_whatsapp_message


@api_view(['GET'])
def check_attendance(request):
    client = request.user.client
    attendance = Attendance.objects.filter(client=client)
    return Response({'attendance': attendance})


@api_view(['GET'])
def view_subscription(request):
    client = request.user.client
    subscription = Subscription.objects.filter(client=client).last()
    return Response({'subscription': subscription})


@api_view(['POST'])
def whatsapp_check_in(request):
    phone_number = request.data.get('phone_number')
    client = Client.objects.get(phone_number=phone_number)

    attendance = Attendance.objects.filter(client=client, check_in_time=timezone.now())

    message = f"HI {Client.user.username}, you have successfully checked in {attendance.check_in_time}."
    send_whatsapp_message(phone_number, message)

    return Response({'status': 'success', 'message': 'Check in successfully'})