from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client


def send_whatsapp_message(to, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=body,
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        to=f'whatsapp:{to}'
    )
    return message.sid


@csrf_exempt
def whatsapp_webhook(request):
    incoming_msg = request.POST.get('Body', '').strip().lower()
    from_number = request.POST.get('From', '')

    response = MessagingResponse()
    msg = response.message()

    if incoming_msg == 'register':
        msg.body('Please provide your username.')
    elif incoming_msg == 'my plan':
        msg.body('You are currently on the premium plan.')
    else:
        msg.body('Sorry, I did not understand that command.')

    return HttpResponse(str(response), content_type='text/xml')