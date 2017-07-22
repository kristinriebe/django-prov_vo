import datetime

from django.utils import timezone
from django.test import TestCase

from .models import Activity, RaveObsids
from django.test import Client
from django.test.utils import setup_test_environment

# Run all tests:
#   python manage.py test
# Run individual tests using:
#   python manage.py test provapp.tests.Activity_TestCase
# or similar


class RaveObsids_TestCase(TestCase):

    rave_obs_id = "20121220_0752m38_089"

    def setUp(self):
        f = RaveObsids.objects.create(rave_obs_id=self.rave_obs_id, obsdate="20121220", platenumber=3)
        f.save()

    def test_getRaveObsid(self):
        qset = RaveObsids.objects.get(rave_obs_id=self.rave_obs_id)
        self.assertEqual(qset.rave_obs_id, self.rave_obs_id)

    def test_getPlatenumber(self):
        qset = RaveObsids.objects.get(rave_obs_id=self.rave_obs_id)
        self.assertEqual(qset.platenumber, u'3')

    def test_reducedFile(self):
        qset = RaveObsids.objects.get(rave_obs_id=self.rave_obs_id)
        result = qset.get_reducedfile(qset.rave_obs_id)
        reduced_file = result['reduced_file']
        #print("reduced_file: ", reduced_file)
        self.assertEqual(reduced_file, u"corvus.aip.de:/store/01/Data_RAVE_s/RAVE/reduced_IRAF/2012/20121220/0752m38.rvsun.fts")

    def test_originalFiles(self):
        qset = RaveObsids.objects.get(rave_obs_id=self.rave_obs_id)
        result = qset.get_originalfiles(qset.rave_obs_id)
        files = result['originalfiles']
        #print("reduced_file: ", reduced_file)
        self.assertEqual(files, u"corvus.aip.de:/store/01/Data_RAVE_s/RAVE_ORIG/20121220/0752m38*.fits")


class Activity_TestCase(TestCase):

    def setUp(self):
        f = Activity.objects.create(id="rave:myid", name="mylabel")
        f.save()

    def test_getActivity(self):
        qset = Activity.objects.get(id="rave:myid")
        #print(qset)
        #print("label: ", qset.label)
        self.assertEqual(qset.name, "mylabel")
