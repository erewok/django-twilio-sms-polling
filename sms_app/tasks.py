import random
# I don't know about you, but when I see this as the first import,
# I think to myself: what the hell is about to happen here?
from itertools import cycle, islice
from celery.task import task
from datetime import timedelta
from django.utils import timezone

from sms_app.models import Messages, Scheduler, Receiver
from sms_app.send_messages.send_messages import send_sms

def get_offset_range(offset_morning, day_length):
    """Given a morning and a day_length, this function
    creates a defined interval of allowable hours, so that
    day and night are easy to define for calculator function.

    Returns: set of integers for quick membership testing:
     -> set([23, 0, 1, 2, 3, etc.])"""
    full_day = range(0, 24)
    night_idx = offset_morning + day_length
    allowed_hours = set(islice(cycle(full_day),
                                offset_morning,
                                night_idx))
    return allowed_hours

def calculate_next_send(send_at, interval=False, day=True, UTC_offset=0):
    if not interval:
        my_rand_int = random.randrange(45, 240, 15)
        next_send = send_at + timedelta(minutes=my_rand_int)
    else:
        next_send = send_at + timedelta(hours=interval)

    if day:
        utc_morning = 8 # set morning
        day_length = 13 # for a range; total hours in a day: 12
        offset_morning = utc_morning + UTC_offset

        if offset_morning < 0:
            offset_morning += 24
        allowed_hours = get_offset_range(offset_morning, day_length)

        while next_send.hour not in allowed_hours:
            my_rand_int = random.randrange(600, 840)
            next_send = send_at + timedelta(minutes=my_rand_int)

    return next_send

## to do:
### this stuff needs to be moved into the model for the message object.
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

def get_utc_offset(msg_object):
    """Returns the first utc_offset of the first recipient associated
    with the message instance. This only works if the message
    instance has recipients with the same utc offset."""
    return msg_object.recipients.values_list('offset')[0][0]

@task
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

    ## Users have no access to scheduler database, so they will be deleting "messages"
    ## Need to delete all sheduled messages where the Message object does not exist
    Scheduler.objects.filter(message_id__send_is_on = False).delete()
    #    Scheduler.objects.filter(message_id = None).delete()


@task
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
        day_send = msg.send_only_during_daytime
        interval = get_send_interval(msg)
        utc_offset = get_utc_offset(msg)

        ## sometimes initial send time will be in the past; in that case, get a new next_send_time
        ## This is particularly the case where users are unaware that Django uses timezone naive
        ## DateTimeFields in Django Admin (where users are storing messages), so
        ## the field in django admin looks like local timezone, which for the US
        ## will be behind UTC. Thus, initial sends will often be in the past.
        ## Solution: set arbitrary init_send for ten minutes in the future
        ## Then, calculate first interval to be sure not to send at night accidentally.

        if msg.init_schedule_time < now:
            dummy_init_time = now + timedelta(minutes=10)
            first_send = calculate_next_send(dummy_init_time,
                                             interval = interval,
                                             day = day_send,
                                             UTC_offset = utc_offset)
        else:
            first_send = msg.init_schedule_time

        next_send_time = calculate_next_send(first_send,
                                             interval = interval,
                                             day = day_send,
                                             UTC_offset = utc_offset)
        scheduled_msg = Scheduler(message_id = msg,
                                      send_at = first_send,
                                      next_send = next_send_time)
        scheduled_msg.save()

@task
def send_scheduled_messages():
    # pull scheduled messages from the database. send them.
    now = timezone.now()
    end = now + timedelta(seconds=210) # for this to work,
    # it needs to spin up just  _AFTER_ this time interval
    for scheduled_msg in Scheduler.objects.filter(
            send_at__gte=now
            ).filter(
                send_at__lte=end):
        if now < scheduled_msg.message_id.stop_time:
            send_sms(scheduled_msg.message_id)
            scheduled_msg.send_at = scheduled_msg.next_send
            # calculate next send
            interval = get_send_interval(scheduled_msg.message_id)
            offset = get_utc_offset(scheduled_msg.message_id)
            day = scheduled_msg.message_id.send_only_during_daytime
            scheduled_msg.next_send = calculate_next_send(scheduled_msg.send_at,
                                                          interval=interval,
                                                          day=day,
                                                          UTC_offset = offset)
            scheduled_msg.save()

        if scheduled_msg.message_id.send_once:
            # schedule msg and set send_is_on to false
            scheduled_msg.message_id.send_is_on = False
            scheduled_msg.message_id.save()
            scheduled_msg.delete()
