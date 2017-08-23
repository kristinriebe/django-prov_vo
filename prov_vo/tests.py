import datetime
import re

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

from django.test import Client
from django.test.utils import setup_test_environment

from .models import Activity, ActivityFlow, HadStep
# Run all tests:
#   python manage.py test
# or:
#   python manage.py test --settings=provenance.test_settings --nomigrations
#
# Run individual tests using:
#   python manage.py test prov_vo.tests.Activity_TestCase
# or similar

class Activity_TestCase(TestCase):

    def setUp(self):
        f = Activity.objects.create(id="rave:myid", name="mylabel")
        f.save()

    def test_getActivity(self):
        qset = Activity.objects.get(id="rave:myid")
        self.assertEqual(qset.name, "mylabel")


class ProvDAL_TestCase(TestCase):

    def setUp(self):
        a = Activity.objects.create(id="rave:act", name="myactivity")
        a.save()
        af = ActivityFlow.objects.create(id="rave:flow", name="myflow")
        af.save()
        h = HadStep.objects.create(activityFlow=af, activity=a)
        h.save()

    def test_getProvdalNoID(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, 'Bad request: the ID parameter is required.')

    def test_getProvdalNothingFound(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=blabla')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        numlines = len(found)
        self.assertEqual(numlines, 0)

    def test_getProvdalActivityFlow(self):
        client = Client()
        #response = client.get(reverse('prov_vo:index'))
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow')
        self.assertEqual(response.status_code, 200)

        expected = 'activityFlow(rave:flow, -, -, [voprov:name="myflow"])'
        found = re.search(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(found.group(0), expected)

    def test_getProvdalActivityFlowDepth2(self):
        client = Client()
        #response = client.get(reverse('prov_vo:index'))
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow'+'&DEPTH=2')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 1)

    def test_getProvdalActivityFlowIncludeSteps(self):
        # If STEPS=TRUE, substeps of the activityFlow shall be followed,
        # thus both, activityFlow and activity must be returned
        client = Client()
        #response = client.get(reverse('prov_vo:index'))
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow'+'&DEPTH=2'+'&STEPS=TRUE')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 2)

    def test_getProvdalActivityDepth2(self):
        client = Client()
        #response = client.get(reverse('prov_vo:index'))
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:act'+'&DEPTH=2')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 2)
