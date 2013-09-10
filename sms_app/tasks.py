import random
# I don't know about you, but when I see this as the first import,
# I think to myself: what the hell is about to happen here?

from datetime import timedelta
from django.utils import timezone
from sms_app.models import Messages, Scheduler
from sms_app.send_messages.send_messages import send_sms


def calculate_next_send(send_at, interval=False, day=True):
    if not interval:
        my_rand_int = random.randrange(45, 240, 15)
        next_send = send_at + timedelta(minutes=my_rand_int)
    else:
        next_send = send_at + timedelta(hours=interval)

    if day is True and next_send.hour < 7 or next_send.hour >= 20:
        while next_send.hour < 7 or next_send.hour >= 20:
            my_rand_int = random.randrange(600, 1020) # switch from interval to random here...
            # make sure to correct on the next send, next day
            next_send = send_at + timedelta(minutes=my_rand_int)
    return next_send

def get_send_interval(msg_object):
    """Basic helper function used by other functions to retrieve send interval or negative
    interval if the message is only supposed to be sent once."""
    if msg_object.send_interval is not None:
        interval = msg_object.send_interval
    else:
        interval = False
    if msg_object.send_once:
        interval = -5
    return interval

def cleanup_expired():
    """cleanup_expired filters table for expired messages (stop_time in past and send_is_on=True)
    Side effect #1: It sets send_is_on=False.
    Side effect #2: It checks if there is a Scheduler table entry
    for the message and deletes it if so."""
    now = timezone.now()
    expired_msgs = Messages.objects.filter(
        stop_time__lt=now).filter(
            send_is_on=True)

    for msg in expired_msgs:
        msg.send_is_on = False ## test this: keeps failing unit testing but it works in shell...?
        msg.save()
        if Scheduler.objects.filter(message_id=msg).exists():
            Scheduler.objects.get(message_id=msg).delete()

    Scheduler.objects.filter(message_id__send_is_on=False).delete()

def schedule_new_messages():
    """schedule_new_messages looks for messages with all of the following constraints:
    send_is_on=True,
    stop_time is in the future,
    scheduler__mesage_id=None (no Scheduler Entry for message)
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
        send_at_time = msg.init_schedule_time
        day_send = msg.send_only_during_daytime
        interval = get_send_interval(msg)
        next_send_time = calculate_next_send(send_at_time, interval=interval, day=day_send)
        scheduled_msg = Scheduler(message_id = msg,
                                      send_at = send_at_time,
                                      next_send = next_send_time)
        scheduled_msg.save()

    ## major problem: it sends in UTC: needs to send with respect to user's local timezone OR
    ## needs to know user's timezone and convert to UTC

def send_scheduled_messages():
    # pull scheduled messages from the database. send them.
    now = timezone.now()
    end = now + timedelta(seconds=200) # for this to work,
    # it needs to spin up just  _AFTER_ this time interval
    for scheduled_msg in Scheduler.objects.filter(send_at__gt=now).filter(send_at__lte=end):
        if now < scheduled_msg.message_id.stop_time:
            send_sms(scheduled_msg.message_id)
            scheduled_msg.send_at = scheduled_msg.next_send
            # calculate next send
            interval = get_send_interval(scheduled_msg.message_id)
            day = scheduled_msg.message_id.send_only_during_daytime
            scheduled_msg.next_send = calculate_next_next_send(scheduled_msg.send_at, interval=interval, day=day)
            scheduled_msg.save()

        if scheduled_msg.message_id.send_once:
            # schedule msg and set send_is_on to false
            scheduled_msg.message_id.send_is_on = False
            scheduled_msg.message_id.save()
            scheduled_msg.delete()
