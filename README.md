sms_random_interval_polling
===========================

Designed to be deployed at Heroku, SMS Random Interval Polling utilizes 
Django and Twilio's REST API to send out SMS messages at either predefined
or random intervals. 

Admin Django users can add Messages to the database and the scheduler
will send them at appropriate times. 

The goals are to randomly sample a population via SMS in order to 
produce solid data for later analysis by researchers. 

This is an unfinished project, with expected completion date of November,
2013.

===========================
Things We Are Working On:

-Finalizing Scheduler
-Supporting time-zone-aware SMS sending
-Exporting survey results
-Building a generic settings.py

===========================
How to Use:

We have not assigned a license to this program yet, but we will (shortly). In the meantime,
if you want to use it, clone the github repo, build a virtualenv to work within, and
set-up a Django project (see the Django docs or Django book). 

Once you have a virtualenv, install requirements listed at requirements.txt:

    pip install -r requirements.txt

The settings.py used for this project is pretty boilerplate but will likely need some editing 
to work. The only other thing needed to make this work is to manually insert your Twilio Account 
details into the database (see instructions below*).

(see sms_app.models.TwilioAccount for model information).

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
   from sms_app.models import TwilioAcct

   my_account = TwilioAcct(auth_token="{YOUR AUTH TOKEN}", account_side="{YOUR ACCOUNT SID"}, number="{NUMBER}")
   my_account.save()

Now your account details can be retrieved to verify incoming texts and to send outgoing
messages via Twilio REST API