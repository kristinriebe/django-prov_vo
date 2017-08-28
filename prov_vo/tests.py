import datetime
import re

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

from django.test import Client
from django.test.utils import setup_test_environment

from .models import Activity, ActivityFlow, HadStep, Entity
from .models import Agent, WasAssociatedWith, WasAttributedTo
# Run all tests:
#   python manage.py test
# or:
#   python manage.py test --settings=provenance.test_settings --nomigrations
#
# Run individual tests using:
#   python manage.py test --settings=provenance.test_settings --nomigrations prov_vo.tests.Activity_TestCase
# or similar


# Model tests
class Activity_TestCase(TestCase):

    def setUp(self):
        f = Activity.objects.create(id="rave:myid", name="mylabel")
        f.save()

    def test_getActivity(self):
        qset = Activity.objects.get(id="rave:myid")
        self.assertEqual(qset.name, "mylabel")

class ActivityFlow_TestCase(TestCase):

    def setUp(self):
        af = ActivityFlow.objects.create(id="rave:flow", name="myflow")
        af.save()

    def test_getActivity(self):
        qset = ActivityFlow.objects.get(id="rave:flow")
        self.assertEqual(qset.name, "myflow")


class Entity_TestCase(TestCase):

    def setUp(self):
        e = Entity.objects.create(id="rave:dr4", name="RAVE DR4")
        e.save()

    def test_getEntity(self):
        qset = Entity.objects.get(id="rave:dr4")
        self.assertEqual(qset.name, "RAVE DR4")


# View tests
class ProvDAL_TestCase(TestCase):

    def setUp(self):
        a = Activity.objects.create(id="rave:act", name="myactivity")
        a.save()
        af = ActivityFlow.objects.create(id="rave:flow", name="myflow")
        af.save()
        h = HadStep.objects.create(activityFlow=af, activity=a)
        h.save()

        e = Entity.objects.create(id="rave:dr4", name="RAVE DR4")
        e.save()

        ag = Agent.objects.create(id="org:rave", name="RAVE project")
        ag.save()
        was = WasAssociatedWith.objects.create(activity=a, agent=ag)
        was.save()
        wat = WasAttributedTo.objects.create(entity=e, agent=ag)
        wat.save()

    # ID is a required parameter
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
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow')
        self.assertEqual(response.status_code, 200)

        expected = 'activityFlow(rave:flow, -, -, [voprov:name="myflow"])'
        found = re.search(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(found.group(0), expected)

    def test_getProvdalActivityFlowDepth2(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow'+'&DEPTH=2')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 1)

    def test_getProvdalActivityFlowIncludeSteps(self):
        # If STEPS=TRUE, substeps of the activityFlow shall be followed,
        # thus both, activityFlow and activity must be returned
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow'+'&DEPTH=2'+'&STEPS=TRUE')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 2)

    def test_getProvdalActivityDepth2(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:act'+'&DEPTH=2')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 2)

    # In this implementation, ID can also take an agent's ID, but agent relations are only
    # followed beyond the agent if AGENT option is set to TRUE
    def test_getProvdalAgent(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=org:rave&DEPTH=1')
        self.assertEqual(response.status_code, 200)
        # only the agent itself should be returned
        found = re.findall(r"^agent.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 1)

    def test_getProvdalAgentFollow(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=org:rave&AGENT=TRUE&DEPTH=1')
        self.assertEqual(response.status_code, 200)
        # agent, activity, entity, wat and was. relation should be returned
        # strip begin/end document and prefix from response content:
        content = re.findall(r"^(?!prefix).*", response.content, flags=re.MULTILINE)
        content = [l for l in content if not l.startswith("document") and not l.startswith("endDocument")]
        agents = [l for l in content if l.startswith("agent")]
        was = [l for l in content if l.startswith("wasAssociatedWith")]
        wat = [l for l in content if l.startswith("wasAttributedTo")]
        entities = [l for l in content if l.startswith("entity")]
        activities = [l for l in content if l.startswith("activity")]
        self.assertEqual(len(agents), 1)
        self.assertEqual(len(was), 1)
        self.assertEqual(len(wat), 1)
        self.assertEqual(len(entities), 1)
        self.assertEqual(len(activities), 1)
