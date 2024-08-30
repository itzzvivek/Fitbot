from django.shortcuts import render
from django.shortcuts import get_list_or_404
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework.decorators import api_view

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from  .models import Client, Attendance, Subscription, GymOwner
from .utils import send_whatsapp_message



@api_view(['POST'])
def register_client(request):
    gym_owner = GymOwner.objects.get(user=request.user)
    phone_number = request.POST.get('phone_number')
    username = request.data.get('username')
    email = request.data.get('email')
    membership_type = request.data.get('membership_type')

    user = User.objects.create(username=username, email=email)
    user.set_unusable_password()
    user.save()

    client = Client.objects.create(gym_owner=gym_owner, user=user, phone_number=phone_number, membership_type=membership_type)
    
    message = f"Welcome, {username}! You have been successfully registered as a {membership_type} member."
    send_whatsapp_message(client, message)

    return Response({'status': 'success', 'message': 'Client registered successfully.'})


@api_view(['POST'])
def check_in(request):
    gym_owner = GymOwner.objects.get(user=request.user)
    phone_number = request.data.get('phone_number')
    client = Client.objects.get(phone_number=phone_number, gym_owner=gym_owner)

    attendance = Attendance.objects.filter(client=client, check_in_time=timezone.now())

    message = f"HI {Client.user.username}, you have successfully checked in {attendance.check_in_time}."
    send_whatsapp_message(phone_number, message)

    return Response({'status': 'success', 'message': 'Check in successfully'})


@api_view(['POST'])
def subscription_status(request):
    gymowner = GymOwner.objects.get(user=request.user)
    phone_number = request.data.get('phone_number')
    client = Client.objects.get(phone_number=phone_number, gymowner=gymowner)
    subscription = Subscription.objects.filter(client=client).last()

    if subscription:
        message = (f"Hi {client.user.username}, your currently subscription plan is {subscription.plan.name}."
                   f"It expires on {subscription.end_date}.")
    else:
        message = "You do not have an active subscription plan."

    send_whatsapp_message(phone_number, message)
    return Response({'status': 'success', 'message': 'subscription status sent.'})


@api_view(['POST'])
def notify_expiring_subscriptions(request):
    gym_owner = GymOwner.objects.get(user=request.user)
    clients = gym_owner.clients.all()
    expiring_clients = []

    for client in clients:
        subscription = Subscription.objects.get(client=client).last()
        if subscription and (subscription.end_date - timezone.now().date()).days() > 7:
            expiring_clients.append(client)
            message = f"HI {client.user.username}, your subscription plan is expiring soon {subscription.end_date}. Please renew it to continue enjoying our services."
            send_whatsapp_message(client.phone_number, message)

    return Response({'status': 'success', 'message': f'{len(expiring_clients)} clients notified about expiring subscription'})


@api_view(['POST'])
def handle_whatsapp_message(request):
    phone_number = request.data.get('from', '').replace('whatsapp:', '')
    message_body = request.data.get('message_body').strip().lower()

    try:
        client = Client.objects.get(phone_number=phone_number)
    except client.DoesNotExist:
        send_whatsapp_message(phone_number, "Sorry, you are not register with us.")
        return Response({'status': 'error', 'message':'Client not found'})

    if message_body == 'check-in':
        return check_in(request)
    elif message_body == 'my_plan':
        return subscription_status(request)
    else:
        send_whatsapp_message(phone_number, "Sorry, I didn't understand that command.")
        return Response({'status': 'error', 'message': 'Invalid command'})
    