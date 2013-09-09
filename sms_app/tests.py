from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from sms_app.models import Scheduler, Messages, Receiver
from sms_app.tasks import cleanup_expired, schedule_new_messages, calculate_next_send


class SchedulerTesting(TestCase):

    def setUp(self):
        self.now = timezone.now()
        self.later = self.now + timedelta(hours=5)
        self.earlier = self.now - timedelta(hours=5)
        self.recvr = Receiver(phone_number='+16195559088', first_name='gym', last_name='bag')
        self.recvr.save()

    def test_data_insert(self):
        pass

    def test_next_send_calculator(self):
        # Goal: next_send should be in the future
        next_send = calculate_next_send(self.now, interval=False, day=True)
        self.assertLess(self.now, next_send)

        #####################################################################
        # Goal: if day=True, it shouldn't return a time between 8pm and 7am...
        almost_night = self.now.replace(hour=19)
        next_send_wInterval = calculate_next_send(self.now, interval=4, day=True)
        next_send_randomInterval = calculate_next_send(self.now, interval=False, day=True)

        # Goal: random or set interval are both set to future
        self.assertLess(almost_night, next_send_wInterval)
        self.assertLess(almost_night, next_send_randomInterval)

        # Goal: It's not set to an hour after 8pm
        self.assertLess(next_send_wInterval.hour, 20)
        self.assertLess(next_send_randomInterval.hour, 20)

        # Goal: It's not set to an hour before 7am
        self.assertGreaterEqual(next_send_wInterval.hour, 7)
        self.assertGreaterEqual(next_send_randomInterval.hour, 7)
        ######################################################################

    def test_cleanup(self):
        # Build a test-message where send_true and msg.stop_time is in the past
        # 1a)  Manually put this message in the scheduler
        # Goals: on cleanup make sure it a) is deleted from schedule and b) that msg.send_is_on is set to false
        test_msg_clean = Messages(init_schedule_time = self.now,
                            send_only_during_daytime = True,
                            stop_time = self.earlier,
                            send_is_on = True)
        test_msg_clean.save()
        new_sched_msg = Scheduler(message_id = test_msg_clean,
                                  send_at = test_msg_clean.init_schedule_time,
                                  next_send = self.later)
        new_sched_msg.save()
        self.assertTrue(
            Scheduler.objects.filter(message_id=new_sched_msg.message_id).exists())

        cleanup_expired()

        if test_msg_clean.send_is_on is True:
            self.fail("Message is still set to send")
            # this one continues to fail
        with self.assertRaises(Scheduler.DoesNotExist):
            Scheduler.objects.get(message_id=test_msg_clean).exists()

    def test_scheduler(self):
        # 1) that send_once has a next_send set to the past
        # 2) That a send-day just before the end of day has a next_send at night
        pass
