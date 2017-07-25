import datetime

from django.utils import timezone
from django.test import TestCase

from .models import Activity
from django.test import Client
from django.test.utils import setup_test_environment

# Run all tests:
#   python manage.py test
# Run individual tests using:
#   python manage.py test prov_vo.tests.Activity_TestCase
# or similar

class Activity_TestCase(TestCase):

    def setUp(self):
        f = Activity.objects.create(id="rave:myid", name="mylabel")
        f.save()

    def test_getActivity(self):
        qset = Activity.objects.get(id="rave:myid")
        #print(qset)
        #print("label: ", qset.label)
        self.assertEqual(qset.name, "mylabel")
