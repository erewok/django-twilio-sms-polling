"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

class GetTest(TestCase):

    def create_fake_gets(self):
        from django.test.client import Client
        tester = Client()
        testuri = "/sms/response/?AccountSid=AC1794c99886e6c49b02862d4e49f0e429&Body=Here%27s+another+reply.&ToZip=11590&FromState=CA&ToCity=GARDEN+CITY&SmsSid=SM5c842b5ac9470b7f8f4c8159cfb7d37d&ToState=NY&To=%2B15162521619&ToCountry=US&FromCountry=US&SmsMessageSid=SM5c842b5ac9470b7f8f4c8159cfb7d37d&ApiVersion=2010-04-01&FromCity=SAN+DIEGO&SmsStatus=received&From=%2B16195495633&FromZip=92134"
        assert tester.get(testuri)
