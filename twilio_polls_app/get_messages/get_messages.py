from datetime import datetime
from twilio_polls_app.models import Receiver, SentMessage, ReceivedMessage

## this function gets called by the sms/views.py file

def lookup_sent_message(number, conv_id):
    '''Look up Receiver based on last ten digts of number, and then look
    up SentMessage based on receiver.

    Function returns receiver object and SentMessage object.'''
    number = number[-10:] # we're just check the last ten digits and not worry formatting
    recvr = Receiver.objects.filter(phone_number__contains=number)[0]
    msg_object = SentMessage.objects.filter(to_number=recvr).order_by('-timestamp')[0]
    msg_object.conv_id = conv_id
    msg_object.save()
    print "Raw receiver object below"
    print "%r" % recvr
    return recvr, msg_object

def log_request(request):
    '''Uses request dictionary to log raw request to database.'''
    ## Wasted work: SmsMessageSid and SmsSid are the same
    from_number = request.GET.get('From', None)
    conv_id = request.GET.get('SmsSid', '1')
    phone, sent_obj = lookup_sent_message(from_number, conv_id)
    log_received = ReceivedMessage(msg_id = request.GET.get('SmsMessageSid', ''),
                                   message_body = request.GET.get('Body', ''),
                                   timestamp = datetime.now(),
                                   from_number = phone,
                                   conv_id = sent_obj)

    log_received.save()
