from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from sms_app.models import Scheduler, Messages, Receiver
from sms_app.tasks import cleanup_expired, schedule_new_messages
from sms_app.tasks import calculate_next_send, get_send_interval


class SchedulerTesting(TestCase):

    def setUp(self):
        self.now = timezone.now()
        self.later = self.now + timedelta(hours=5)
        self.earlier = self.now - timedelta(hours=5)
        self.almost_night = self.now.replace(hour=19)

        self.rcvr_offset1 = Receiver(phone_number = '+16195559088',
                                  first_name = 'gym',
                                  last_name = 'bag',
                                  offset = -7)
        self.rcvr_offset1.save()

        self.rcvr_offset2 = Receiver(phone_number = '+16195559088',
                                  first_name = 'gym',
                                  last_name = 'bag',
                                  offset = 7)
        self.rcvr_offset2.save()



    def test_data_insert(self):
        self.recvr_one = Receiver(phone_number = '+16195559088',
                                  first_name = 'gym',
                                  last_name = 'bag',
                                  offset = 0)
        self.recvr_one.save()

    def test_next_send_calculator(self):
        # Goal: next_send should be in the future
        next_send = calculate_next_send(self.now, interval=False, day=True)
        self.assertLess(self.now, next_send)

        #####################################################################
        # Goal: if day=True, it shouldn't return a time between 8pm and 7am...
        next_send_wInterval = calculate_next_send(self.now, interval=4, day=True)
        next_send_randomInterval = calculate_next_send(self.now, interval=False, day=True)

        # Goal: random or set interval are both set to future
        self.assertLess(self.almost_night, next_send_wInterval)
        self.assertLess(self.almost_night, next_send_randomInterval)

        # Goal: It's not set to an hour after 8pm
        self.assertLess(next_send_wInterval.hour, 20)
        self.assertLess(next_send_randomInterval.hour, 20)

        # Goal: It's not set to an hour before 8am
        self.assertGreaterEqual(next_send_wInterval.hour, 7)
        self.assertGreaterEqual(next_send_randomInterval.hour, 7)

        #############################################################
        # Goal: if you pass in a negative interval,
        # it should return a next_send earlier than this one
        next_send_day_once = calculate_next_send(self.now, interval=-5, day=True)
        next_send_once = calculate_next_send(self.now, interval=-5, day=False)

        self.assertLess(next_send_day_once, self.now)
        self.assertLess(next_send_once, self.now)
        #############################################################

    def test_utc_offset_calculator(self):
        from sms_app.tasks import get_offset_range
        offset1, offset1_allowed = -9, get_offset_range((8 - 9 + 24), 13)
        offset2, offset2_allowed = -5, get_offset_range((8 - 5), 13)
        offset3, offset3_allowed = 4, get_offset_range(4, 13)

        one_at_offset = self.now + timedelta(hours=offset1)
        offset_next_send1 = calculate_next_send(one_at_offset,
                                               interval=False,
                                               day=True,
                                               UTC_offset=offset1)

        self.assertTrue(offset_next_send1.hour in offset1_allowed)

        two_at_offset = self.now + timedelta(hours=offset2)
        offset_next_send2 = calculate_next_send(two_at_offset,
                                               interval=False,
                                               day=True,
                                               UTC_offset=offset2)
        self.assertTrue(offset_next_send2.hour in offset2_allowed)

        three_at_offset = self.now + timedelta(hours=offset3)
        offset_next_send3 = calculate_next_send(three_at_offset,
                                               interval=False,
                                               day=True,
                                               UTC_offset=offset3)
        self.assertTrue(offset_next_send3.hour in offset3_allowed)


    def test_scheduler(self):
        # One should be scheduled because its stop_time is in the future
        self.test_msg_one = Messages(init_schedule_time = self.now,
                            send_only_during_daytime = True,
                            stop_time = self.later,
                            send_is_on = True)
        self.test_msg_one.save()

        # Two should /not/ be scheduled because its stop time is in the past
        self.test_msg_two = Messages(init_schedule_time = self.now,
                    send_only_during_daytime = True,
                    stop_time = self.earlier,
                    send_is_on = True)
        self.test_msg_two.save()

        # Three should be scheduled and then have a next_send_time in the past
        # because three has the attribute send_once set to True
        self.test_msg_three = Messages(init_schedule_time = self.now,
                    send_only_during_daytime = True,
                    stop_time = self.later,
                    send_once = True,
                    send_is_on = True)

        self.test_msg_three.save()

        self.test_msg_one.recipients.add(self.rcvr_offset1, self.rcvr_offset2)
        self.test_msg_two.recipients.add(self.rcvr_offset1, self.rcvr_offset2)
        self.test_msg_three.recipients.add(self.rcvr_offset1, self.rcvr_offset2)

        self.test_msg_one.save()
        self.test_msg_two.save()
        self.test_msg_three.save()

        schedule_new_messages() # should insert one and three.
        self.assertTrue(Scheduler.objects.filter(message_id=self.test_msg_one).exists())
        self.assertTrue(Scheduler.objects.filter(message_id=self.test_msg_three).exists())

        # the third message should have a next_send set to the past
        scheduled_three = Scheduler.objects.get(message_id=self.test_msg_three)
        self.assertLess(scheduled_three.next_send, self.now)
        # FAILED ONCE AND THEN NOT AGAIN?#

        # should not insert second message where stop time is earlier than now
        self.assertFalse(Scheduler.objects.filter(message_id=self.test_msg_two).exists())


    def test_cleanup(self):
        # Build a test-message where send_true and msg.stop_time is in the past
        # 1a)  Manually put this message in the scheduler
        # Goals: on cleanup make sure it a) is deleted from schedule,
        # and b) that msg.send_is_on is set to false
        test_msg_clean = Messages(init_schedule_time = self.now,
                            send_only_during_daytime = True,
                            stop_time = self.later,
                            send_is_on = True)
        test_msg_clean.save()
        test_msg_clean.recipients.add(self.rcvr_offset1)
        test_msg_clean.save()
        
        schedule_new_messages()
        self.assertTrue(Scheduler.objects.filter(message_id=test_msg_clean).exists())

        test_msg_clean.stop_time = self.earlier
        test_msg_clean.save()

        cleanup_expired()

        if test_msg_clean.send_is_on is True:
            self.fail("Message is still set to send")

        with self.assertRaises(Scheduler.DoesNotExist):
            Scheduler.objects.get(message_id=test_msg_clean).exists()
