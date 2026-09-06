from twilio.rest import Client


def send_whatsapp(account_sid, api_key, api_secret, from_number, to_number, body, auth_token=None):
    """Send a WhatsApp message through Twilio.

    API Key + API Secret are preferred. Auth Token is supported as a fallback.
    Both `from_number` and `to_number` should use the `whatsapp:+...` format.
    """
    if not account_sid or not from_number or not to_number:
        raise RuntimeError("Twilio WhatsApp configuration is missing")

    if api_key and api_secret:
        client = Client(api_key, api_secret, account_sid=account_sid)
    elif auth_token:
        client = Client(account_sid, auth_token)
    else:
        raise RuntimeError("Set TWILIO_API_KEY/TWILIO_API_SECRET or TWILIO_AUTH_TOKEN")

    to_number = str(to_number).strip()
    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"

    from_number = str(from_number).strip()
    if not from_number.startswith("whatsapp:"):
        from_number = f"whatsapp:{from_number}"

    message = client.messages.create(
        body=body,
        from_=from_number,
        to=to_number,
    )
    return message.sid
