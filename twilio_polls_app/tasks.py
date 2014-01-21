import random
# I don't know about you, but when I see this as the first import,
# I think to myself: what the hell is about to happen here?
from itertools import cycle, islice
from celery.task import task
from datetime import timedelta
from django.utils import timezone

from sms_app.models import Messages, Scheduler
from sms_app.send_messages.send_messages import send_sms

class SmartScheduler(object):

    def __init__(self, msg_instance):
        self.msg_instance = msg_instance
        
        ################################
        ## Message Attributes ##
        ################################
        self.day_only = self.msg_instance.send_only_during_daytime
        self.interval = self.msg_instance.send_interval
        self.send_once = self.msg_instance.send_once
        self.utc_offset = self.msg_instance.offset

        ################################
        ## Day Settings ##
        ################################
        # NOTE: set day_length to adjust evening start time #
        self.day_length = 12 
        self.morning = 8
        self.allowed_hours = self._get_offset_range()

    def _get_offset_range(self):
        """This method creates a defined interval of
        allowable hours, so that timezone day/night can be 
        quickly ascertained for calculator function.

        Returns: set of integers for quick membership testing:
         -> set([23, 0, 1, 2, 3, etc.])"""

        offset_morning = self.morning - self.utc_offset
        if offset_morning < 0:
            offset_morning += 24

        full_day = xrange(0, 24)
        night_idx = offset_morning + self.day_length
        allowed_hours = set(islice(cycle(full_day),
                                    offset_morning,
                                    night_idx))
        return allowed_hours

    def calculate_next_send(self, send_at):
        self.send_at = send_at
        
        if not self.interval:
            rand_interval = random.randrange(75, 240)
            next_send = self.send_at + timedelta(minutes=rand_interval)
        else:
            next_send = self.send_at + timedelta(hours=self.interval)

        if self.day_only:
            while next_send.hour not in self.allowed_hours:
                rand_interval = random.randrange(100, 1080)
                next_send = self.send_at + timedelta(minutes=rand_interval)
        return next_send

    def build_schedule(self, send_time = None):
        """Tests for various conditions and
        sets the following attributes for the Scheduler object:

        self.first_send
        self.next_send."""
        
        self.send_time = send_time
        now = timezone.now()
        if self.send_time is None:
            self.send_time = self.msg_instance.init_schedule_time

        if self.send_time < now:
            self.send_time = now + timedelta(minutes=30)
            
        if self.day_only and self.send_time.hour not in self.allowed_hours:
            self.send_time = self.calculate_next_send(self.send_time)

        if self.send_once:
            self.next_send = self.send_time - timedelta(hours = 5)

        else:
            self.next_send = self.calculate_next_send(self.send_time)


@task
def cleanup_expired():
    """cleanup_expired filters table for expired messages
    (stop_time in past and send_is_on=True)
    Side effects:
    a) It sets send_is_on=False, and
    b) It deletes the scheduler object for the message."""
    now = timezone.now()
    expired_msgs = Messages.objects.filter(
        stop_time__lt=now
        ).filter(
            send_is_on=True)

    for msg in expired_msgs:
        msg.send_is_on = False
        msg.save()
        if Scheduler.objects.filter(message_id=msg).exists():
            Scheduler.objects.get(message_id=msg).delete()

@task
def schedule_new_messages():
    """schedule_new_messages looks for messages with
    the following constraints:

    a) send_is_on = True,
    b) stop_time is in the future, and
    c) no Scheduler Entry exists for message object,

    It then schedules those messages in the Scheduler table."""
    now = timezone.now()
    unscheduled_msgs = Messages.objects.filter(
        send_is_on=True
        ).filter(
            stop_time__gt=now
            ).filter(
                    scheduler__message_id=None
                    )

    for msg in unscheduled_msgs:
        smart_msg = SmartScheduler(msg)
        smart_msg.build_schedule()
        scheduled_msg = Scheduler(message_id = msg,
                                      send_at = smart_msg.send_time,
                                      next_send = smart_msg.next_send)
        scheduled_msg.save()

@task
def send_scheduled_messages():
    # pull scheduled messages from the database. send them.
    now = timezone.now()
    end = now + timedelta(seconds=218)
    # this task must spin up just  _AFTER_ this time interval
    for scheduled_msg in Scheduler.objects.filter(
            send_at__gte=now
            ).filter(
                send_at__lte=end
        ).select_related('message_id'):
        
        if now < scheduled_msg.message_id.stop_time:
            send_sms(scheduled_msg.message_id)
            
        if scheduled_msg.message_id.send_once:
            scheduled_msg.message_id.send_is_on = False
            scheduled_msg.message_id.save()
            scheduled_msg.delete()

        else:
            scheduled_msg.send_at = scheduled_msg.next_send            
            # calculate next send -->
            smart_msg = SmartScheduler(scheduled_msg.message_id)
            smart_msg.build_schedule(send_time = scheduled_msg.send_at)
            scheduled_msg.next_send = smart_msg.next_send
            scheduled_msg.save()


