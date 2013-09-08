class TimeIntervalTest(TestCase):
    def test_time_interval(self):
        from sms_app.tasks import calculate_next_send
        from django.utils import timezone
        now = timezone.now()
        next_send = calculate_next_send(now, interval=False, day=True)

        self.failUnless() #...
        # test the following:
        # that send_once has a next_send set to the past
        # that the result is in the future now < next_send
        # that the result is NOT between 9pm and 7am if day is set to true
        # that the result with an interval meets same criteria


class SchedulerTesting(TestCase):
    def help_tasks(self):
        message_model  = '''model values:
        send_once = models.BooleanField()
        send_only_during_daytime = models.BooleanField(verbose_name="Daytime Only")
        send_interval = models.PositiveSmallIntegerField(null=True, blank=True)
        stop_time = models.DateTimeField(null=True, blank=True, verbose_name="Do not send after")
        recipients = models.ManyToManyField(Receiver)
        message_body = models.TextField(null=True, blank=True, verbose_name="Message Body")
        send_is_on = models.BooleanField(verbose_name="Activate Sending?")'''

        scheduler_model = '''class Scheduler(models.Model)
        message_id = models.ForeignKey(Messages)
        send_at = models.DateTimeField()
        next_send = models.DateTimeField()'''
        print(message_model)

    def test_scheduler(self):
        from sms_app.models import Scheduler, Messages, Receiver
        from sms_app.tasks import schedule_messages
        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        later = now + timedelta(interval=5)
        earlier = now - timedelta(interval=5)
        # 1)
        # build a test-message where send_true and msg.stop_time is in the past
        # 1a)  Manually put this message in the scheduler
        # Goals: make sure it a) does not schedule and b) that msg.send_is_on is set to false
        # and finally c) that it has been deleted from the scheduler

        test_msg = Messages(init_schedule_time=now,
                            send_only_during_daytime=True,
                            stop_time=earlier,
                            recipients=Receiver.objects.all()[0],
                            send_is_on=True)


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

