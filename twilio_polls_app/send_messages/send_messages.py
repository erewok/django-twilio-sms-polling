import datetime
from sms_app.models import TwilioAcct, SentMessage
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException

twil_account = TwilioAcct.objects.get(id=1L)
client = TwilioRestClient(twil_account.account_sid, twil_account.auth_token)

def send_sms(message_instance):
    twil_message = client.sms.messages
    msg_body = message_instance.message_body
    for conv_id, recipient in enumerate(message_instance.recipients.all(), 1):
        try:
            msg = twil_message.create(to=format(recipient.phone_number),
                                 from_=twil_account.our_number,
                                 body=msg_body)
            # message is queued immediately...
            print "%s: %s" % (msg.sid, msg.status)
            
            # message is logged in database here
            log_msg = SentMessage(msg_id=msg.sid,
                                  to_number = recipient,
                                  conv_id = conv_id,
                                  message_body = msg_body,
                                  status = "sent",
                                  timestamp = datetime.datetime.now())
            log_msg.save()
        except TwilioRestException as e:
            print e
            log_msg = SentMessage(msg_id="Failed Message",
                                  to_number = recipient,
                                  conv_id = conv_id,
                                  message_body = msg_body,
                                  status = str(e)[:21],
                                  timestamp = datetime.datetime.now())
            log_msg.save()
