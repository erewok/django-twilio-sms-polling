twilio-polls-app
===========================

Designed to be deployed at Heroku, the Django-Twilio Polling App utilizes 
Django and Twilio's REST API to send out SMS messages at either predefined
or random intervals. 

Admin Django users can add Messages to the database and the scheduler
will send them at appropriate times. 

The goals are to randomly sample a population via SMS in order to 
produce solid data for later analysis by researchers. 

===========================
How to Use:

We have not assigned a license to this program yet, but we will (shortly). In the meantime,
if you want to use it, clone the github repo, build a virtualenv to work within, and
set-up a Django project (see the Django docs or Django book). 

Once you have a virtualenv, install requirements listed at requirements.txt:

    pip install -r requirements.txt


Place the file `twilio_poll_settings.py` in the same directory as your settings.py.

Edit your settings.py to include the following:

	from twilio_poll_settings import *


===========================
Instructions on Adding a Twilio Account to the database

In order to send and receive texts, you will need a Twilio account. Go to Twilio.com and 
set one up. On your account information page, you will find an auth token (click the lock)
and an account sid. There will also be a number assigned to your account in the form:

    "+1\d{10}"  

Keep this format in mind because you will need to use it to add receivers to your database.

To add your Twilio Account details to your database and after setting-up your 
Django project, do the following:

   python manage.py syncdb
   python manage.py shell
   from twilio_polls_app.models import TwilioAcct

   my_account = TwilioAcct(auth_token="{YOUR AUTH TOKEN}", account_side="{YOUR ACCOUNT SID"}, number="{NUMBER}")
   my_account.save()

Now your account details can be retrieved to verify incoming texts and to send outgoing
messages via Twilio REST API
