from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import Http404


from .models import ResponseMessages, TwilioAcct
from .get_messages import get_messages


def sms_main(request):
   return render_to_response('sms/main.html')

def sms_response(request):
   '''Retrieve and execute the TwiML at this URL via the selected HTTP method (GET)
   when this application receives a message.'''
   twil_account = TwilioAcct.objects.get(id=1L)
   if request.method == 'GET':
      if 'AccountSid' in request.GET and request.GET['AccountSid'] == twil_account.account_sid:
         get_messages.log_request(request)
         text_response = ""
         for item in ResponseMessages.objects.all():
            if item.active:
               text_response += item.response_message
         return render_to_response('sms/response.xml', {'response' : text_response})
      else:
        raise Http404

def sms_fallback(request):
   '''Retrieve and execute the TwiML at this URL when the Messaging Request URL
   above can\'t be reached or there is a runtime exception.'''
   ##THIS doesn't attempt to log the request##
   ## IT (will eventually) initiate error handling to try to track down the
   ## reason we are falling back here
   text_response = ""
   for item in ResponseMessages.objects.all():
      if item.active:
         text_response += item.response_message
         
   return render_to_response('sms/fallback.xml', {'response' : text_response})

def sms_status_callback(request):
   '''Make a POST request to this URL when a REST API request to send an outgoing
   message has either succeeded or failed'''
   pass
