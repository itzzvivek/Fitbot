from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.request import Request
from twilio.rest import Client

from .models import Client, Attendance, Subscription, GymOwner
from .utils import send_whatsapp_message


@api_view(['POST'])
def register_gym(request):
    username = request.data.get('username')
    gym_name = request.data('gym_name')
    email = request.data('email')
    contact_number = request.data('contact_number')

    if User.objects.filter(username=username).exists():
        return Response({'status': 'error', 'message': 'Username already exists.'})

    user = User.objects.create_user(username=username, email=email,
                                    contact_number=contact_number)
    gym_owner = GymOwner.objects.create(user=user, name=gym_name)
    message = f"Welcome {gym_owner.gym_name}! You have successfully registered."
    send_whatsapp_message(contact_number, message)
    return Response({'status': 'success', 'message': 'Gym registered successfully.'})


@api_view(['POST'])
def register_client(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    phone_number = request.POST.get('phone_number')
    email = request.data.get('email')
    membership_type = request.data.get('membership_type')

    # try:
    #     gym_owner = GymOwner.objects.get(gym_name=gym_name)
    # except GymOwner.DoesNotExist:
    #     return Response({'status': 'error', 'message': 'Gym not found'})

    user = User.objects.create(first_name=first_name, last_name=last_name, email=email)
    user.set_unusable_password()
    user.save()

    client = Client.objects.create(user=user, phone_number=phone_number,
                                   membership_type=membership_type)
    
    message = f"Welcome, {first_name}! You have been successfully registered as a {membership_type} member."
    send_whatsapp_message(settings.TWILIO_WHATSAPP_NUMBER_TO, message)

    return Response({'status': 'success', 'message': 'Client registered successfully.'})


@api_view(['POST'])
def check_in(request):
    # gym_owner = GymOwner.objects.get(user=request.user)
    phone_number = request.data.get('phone_number')
    client = Client.objects.get(phone_number=phone_number)

    attendance = Attendance.objects.filter(client=client, check_in_time=timezone.now())

    message = f"HI {Client.user.username}, you have successfully checked in {attendance.check_in_time}."
    send_whatsapp_message(phone_number, message)

    return Response({'status': 'success', 'message': 'Check in successfully'})


@api_view(['POST'])
def subscription_status(request):
    # gymowner = GymOwner.objects.get(user=request.user)
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


# @api_view(['POST'])
# def notify_expiring_subscriptions(request):
#     # gym_owner = GymOwner.objects.get(user=request.user)
#     clients = gym_owner.clients.all()
#     expiring_clients = []
#
#     for client in clients:
#         subscription = Subscription.objects.get(client=client).last()
#         if subscription and (subscription.end_date - timezone.now().date()).days() > 7:
#             expiring_clients.append(client)
#             message = (f"HI {client.user.username}, your subscription plan is expiring soon {subscription.end_date}. "
#                        f"Please renew it to continue enjoying our services.")
#             send_whatsapp_message(client.phone_number, message)
#
#     return Response({'status': 'success', 'message': f'{len(expiring_clients)} '
#                                                      f'clients notified about expiring subscription'})


@csrf_exempt
@api_view(['POST'])
def handle_whatsapp_message(request):
    phone_number = request.data.get('From', '').replace('whatsapp:', '')
    message_body = request.data.get('Body', '').strip().lower()

    # Check if the registration process has started
    registration_stage = request.session.get('registration_stage')

    if registration_stage is None and message_body == 'register-client':
        request.session['registration_stage'] = 'first_name'
        send_whatsapp_message(phone_number, "Please provide your first name.")
        return Response({'status': 'success', 'message': 'Asking for first name'})
    
    elif registration_stage == 'first name':
        request.session['first name'] = message_body
        request.session['registration_stage'] = 'last_name'
        send_whatsapp_message(phone_number, "Thank you! Now, please provide your full name.")
        return Response({'status': 'success', 'message': 'Asking for last name'})

    elif registration_stage == 'last name':
        request.session['last name'] = message_body
        request.session['registration_stage'] = 'email'
        send_whatsapp_message(phone_number, "Great! Now, please provide your email address.")
        return Response({'status': 'success', 'message': 'Asking for email'})

    elif registration_stage == 'phone number':
        request.session['phone number'] = message_body
        request.session['registration_stage'] = 'address'
        send_whatsapp_message(phone_number, "Awesome! Now, please provide your address.")
        return Response({'status': 'success', 'message': 'Asking for address'})

    elif registration_stage == 'address':
        Client.objects.create(
            phone_number=phone_number,
            username=request.session['username'],
            full_name=request.session['full_name'],
            email=request.session['email'],
            address=message_body
        )
        send_whatsapp_message(phone_number, "Thank you for registering! Your details have been saved.")
        request.session.flush()  # Clear the session
        return Response({'status': 'success', 'message': 'Client registered successfully'})

    else:
        send_whatsapp_message(phone_number, "Sorry, I didn't understand that command. "
                                            "Please type 'register client' to start the registration process.")
        return Response({'status': 'error', 'message': 'Invalid command'})


    