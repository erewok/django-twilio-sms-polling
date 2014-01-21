from django.db import models

### PRIMARY DATA ###

class Receiver(models.Model):
    phone_number = models.CharField(max_length=17, primary_key=True, verbose_name='phone number')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    offset = models.SmallIntegerField(verbose_name="UTC Offset")

    def __unicode__(self):
        return "%s with utc offset: %r" % (self.phone_number, self.offset)

    def __str__(self):
        return "%s with utc offset: %r" % (self.phone_number, self.offset)

### SMS LOGIC DATA ###

class SentMessage(models.Model):
    msg_id = models.CharField(max_length=50)
    to_number = models.ForeignKey(Receiver)
    conv_id = models.CharField(max_length=50)
    message_body = models.TextField()
    status = models.CharField(max_length=20)
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return self.msg_id

    def __str__(self):
        return "%s" % self.msg_id

class ReceivedMessage(models.Model):
    msg_id = models.CharField(max_length=60)
    from_number = models.ForeignKey(Receiver)
    conv_id = models.ForeignKey(SentMessage)
    message_body = models.TextField()
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return self.msg_id

    def __str__(self):
        return "%s" % self.msg_id

### WEB INTERFACE MODElS & MESSAGE MODELS ###
### MESSAGES MODEL IS CORE DATA UNIT IN THIS PROGRAM ###

class Messages(models.Model):
    init_schedule_time = models.DateTimeField(null=True, blank=True, verbose_name="Poll Start Time")
    send_once = models.BooleanField()
    send_only_during_daytime = models.BooleanField(verbose_name="Daytime Only")
    send_interval = models.PositiveSmallIntegerField(null=True, blank=True,
                                                     verbose_name="Interval (hrs): Leave blank for random interval")
    stop_time = models.DateTimeField(null=True, blank=True, verbose_name="Message Expiry")
    recipients = models.ManyToManyField(Receiver)
    message_body = models.CharField(max_length=160, null=True, blank=True, verbose_name="Message Body")
    send_is_on = models.BooleanField(verbose_name="Message Activated")

    def _get_send_interval(self):
        """Basic helper function used to check and set interval
        to an integer value."""
        if self.send_interval is not None:
            interval = self.send_interval
        else:
            interval = 0
        return interval
    interval = property(_get_send_interval)

    def _get_utc_offset(self):
        """Returns the first utc_offset of the first recipient associated
        with the message instance. This only works if the message
        instance has recipients with the same utc offset."""
        return self.recipients.all()[0].offset
    offset = property(_get_utc_offset)

    def __unicode__(self):
        return "Message object: %s, Send Activated: %s" % (self.id, self.send_is_on)

    class Meta:
        verbose_name = u"Messages"
        verbose_name_plural = u"Messages"

class ResponseMessages(models.Model):
    active = models.BooleanField()
    response_message = models.CharField(max_length=160)

    def __unicode__(self):
        return "%s %s" % (self.response_message, self.active)

## ACCOUNT INFORMATION ##

class TwilioAcct(models.Model):
    account_sid = models.CharField(max_length=40)
    auth_token = models.CharField(max_length=40)
    our_number = models.CharField(max_length=17)

## MESSAGE SCHEDULING LOGIC ##

class Scheduler(models.Model):
    message_id = models.OneToOneField(Messages)
    send_at = models.DateTimeField()
    next_send = models.DateTimeField()

    def __unicode__(self):
        return "Scheduled: %s" % self.message_id
