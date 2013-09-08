sms_random_interval_polling
===========================

App for sending SMS messages at random intervals for purposes of surveying participants

This app was created with Django and Twilio. 

It relies on Celery for scheduling
and Django admin for users to insert polling messages.

To get it going, a Twilio account must be manually added to the database
(see sms_app.models.TwilioAccount for model information).
