import random # I don't know about you, but when I see this as the first import,
# I think to myself: what the hell is about to happen here?

from datetime import datetime, timedelta
from django.utils import timezone
from celery import task, Celery
from sms_app.models import Messages, Scheduler

def help_tasks():
        def help_tasks(self):
            message_model  = '''model values:
            send_once = models.BooleanField()
            send_only_during_daytime = models.BooleanField(verbose_name="Daytime Only")
            send_interval = models.PositiveSmallIntegerField(null=True, blank=True,
                                                         verbose_name="Interval (hrs): Leave blank for random interval")
            stop_time = models.DateTimeField(null=True, blank=True, verbose_name="Do not send after")
            recipients = models.ManyToManyField(Receiver)
            message_body = models.TextField(null=True, blank=True, verbose_name="Message Body")
            send_is_on = models.BooleanField(verbose_name="Activate Sending?")'''

            scheduler_model = '''class Scheduler(models.Model)
            message_id = models.ForeignKey(Messages)
            send_at = models.DateTimeField()
            next_send = models.DateTimeField()'''
            print(message_model)
            print(scheduler_model)

def calculate_next_send(send_at, interval=False, day=True):
    ## major problem: it sends in UTC: needs to send with respect to user's local timezone
    if not interval:
        my_rand_int = random.randrange(45, 240, 15)
        next_send = send_at + timedelta(minutes=my_rand_int)
    else:
        if not isinstance(interval, int):
            int(interval)
        next_send = send_at + timedelta(hours=interval)

    if day is True and next_send.hour < 7 or next_send.hour >= 21:
        while next_send.hour < 7 or next_send.hour >= 21:
            my_rand_int = random.randrange(600, 1020) # swith from interval to random here...
            next_send = send_at + timedelta(minutes=my_rand_int)
        # make sure to check on sending that stop-time is NOT before send_at
    return next_send

def schedule_messages():
    """
    Logic:
        retrieve msgs where msg.send_is_on=True
        1) if stop time in future and msg is not in Scheduler table: schedule it
        2) clean-up to make sure that stop times in past have send_is_on set to False
        and msg has been removed from scheduler table
        3) if message is "send_once", scheduler it once and make sure interval is negative
        !and make sure that works! so that "next_send" is prior to send_at
    date_format = "%d/%m/%Y %H:%M:%S"
    """
    msgs = Messages.objects.filter(send_is_on=True)
    now = timezone.now()
    for msg in msgs:
        if now > msg.stop_time:
            msg.send_is_on = False
            msg.save()
            if Scheduler.objects.filter(message_id=msg).exists():
                Scheduler.objects.get(message_id=msg).delete()

        elif now < msg.stop_time and not Scheduler.objects.filter(message_id=msg).exists():
            ## initial schedule
            send_at_time = msg.init_schedule_time
            day_send = msg.send_only_during_daytime
            if msg.send_interval is not None:
                interval = msg.send_interval
            else:
                interval = False
            if msg.send_once:
                interval = -5 # test next_send to make sure next_time is in the past
            next_send_time = calculate_next_send(send_at_time, interval=interval, day=day_send)
            scheduled_msg = Scheduler(message_id = msg,
                                      send_at = send_at_time,
                                      next_send = next_send_time)
            scheduled_msg.save()



def send_messages_to_worker():
    # pull scheduled messages from the database. send them.
    now = timezone.now()
    start = now + timedelta(seconds=110) # is this necessary?
    for msg in Scheduler.objects.filter(send_at) == filter(date__range): ## this is probably not what I want
        pass


    if now < msg.stop_time: ## what to do next?
        sched_msg = Scheduler.objects.filter(message_id=msg)
            # think about the logic...
            # message is already scheduled, do we need to update next send time? maybe the send scheduler can do that?


    if msg.send_once:
        # schedule msg and set send_is_on to false
        # use the stop time up above. set it to just after
        x.send_is_on = False
        x.save()

            ## next task: spin up and update all to-be-sent-messages

