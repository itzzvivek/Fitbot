from twilio.rest import Client
from django.conf import settings


def send_whatsapp_message(to, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=body,
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        to=f'whatsapp:{to}'
    )
    return message.sid