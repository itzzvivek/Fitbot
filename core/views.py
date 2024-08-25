from django.shortcuts import render
from django.shortcuts import get_list_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from  .models import Client, Attendance, Subscription
from .utils import send_whatsapp_message


@api_view(['POST'])
def register_client(request):
    phone_number = request.POST.get('phone_number')
    username = request.data.get('username')
    email = request.data.get('email')
    membership_type = request.data.get('membership_type')

    user = User.objects.create(username=username, email=email)
    user.set_unusable_password()
    user.save()

    client = Client.objects.create(user=user, phone_number=phone_number, membership_type=membership_type)
    
    message = f"Welcome, {username}! You have been successfully registered as a {membership_type} member."
    send_whatsapp_message(client, message)

    return Response({'status': 'success', 'message': 'Client registered successfully.'})

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


@api_view(['POST'])
def whatsapp_subscription_status(request):
    phone_number = request.data.get('phone_number')
    client = Client.objects.get(phone_number=phone_number)
    subscription = Subscription.objects.filter(client=client).last()

    if subscription:
        message = (f"Hi {client.user.username}, your currently subscription plan is {subscription.plan.name}."
                   f"It expires on {subscription.end_date}.")
    else:
        message = "You do not have an active subscription plan."

    send_whatsapp_message(phone_number, message)
    return Response({'status': 'success', 'message': 'subscription status sent.'})


@api_view(['POST'])
def handle_whatsapp_message(request):
    phone_number = request.data.get('phone_number')
    message_body = request.data.get('message_body').strip().lower()

    if message_body == 'check-in':
        return whatsapp_check_in(request)
    elif message_body == 'my_plan':
        return whatsapp_subscription_status(request)
    else:
        send_whatsapp_message(phone_number, "Sorry, I didn't understand that command.")
        return Response({'status': 'error', 'message': 'Invalid command'})
    