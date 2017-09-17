import datetime
import re
import json

from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

from django.test import Client
from django.test.utils import setup_test_environment

from prov_vo.models import Activity, ActivityFlow, HadStep
from prov_vo.models import Entity, WasGeneratedBy, Used, WasDerivedFrom, WasInformedBy, HadMember
from prov_vo.models import Agent, WasAssociatedWith, WasAttributedTo
#from prov_vo.urls import *

# Run all tests:
#   python manage.py test prov_vo
# or:
#   python manage.py test --settings=provenance.test_settings --nomigrations prov_vo
#
# or for using coverage:
#   coverage run --source=prov_vo manage.py test --settings=provenance.test_settings --nomigrations prov_vo
#   coverage report
#
# Run individual tests using:
#   python manage.py test --settings=provenance.test_settings --nomigrations prov_vo.tests.Activity_TestCase
# or similar

def get_content(response):
    content = re.sub(r'document.*\n', '', response.content)
    content = re.sub(r'endDocument', '', content)
    content = re.sub(r'prefix.*\n', '', content)

#    print 'content: \n', content
    return content


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


class Agent_TestCase(TestCase):

    def setUp(self):
        a = Agent.objects.create(id="ex:ag1", name="Max Maier")
        a.save()

    def test_getAgent(self):
        qset = Agent.objects.get(id="ex:ag1")
        self.assertEqual(qset.name, "Max Maier")


class Used_TestCase(TestCase):

    def setUp(self):
        e = Entity.objects.create(id="rave:pipeline", name="RAVE Pipeline")
        e.save()
        a = Activity.objects.create(id="rave:act", name="myactivity")
        a.save()
        u = Used.objects.create(activity=a, entity=e)
        u.save()

    def test_getUsed(self):
        qset = Used.objects.get(entity="rave:pipeline")
        self.assertEqual(qset.entity.name, "RAVE Pipeline")
        self.assertEqual(qset.activity.id, "rave:act")


class WasGeneratedBy_TestCase(TestCase):

    def setUp(self):
        e = Entity.objects.create(id="rave:data", name="RAVE data")
        e.save()
        a = Activity.objects.create(id="rave:act", name="myactivity")
        a.save()
        wg = WasGeneratedBy.objects.create(activity=a, entity=e)
        wg.save()

    def test_getWasGeneratedBy(self):
        qset = WasGeneratedBy.objects.get(entity="rave:data")
        self.assertEqual(qset.entity.name, "RAVE data")
        self.assertEqual(qset.activity.id, "rave:act")


# View tests
# ==========
class ProvDAL_Accept_TestCase(TestCase):

    def setUp(self):
        a = Entity.objects.create(id="ex:ent", name="An example entity")
        a.save()

    def test_get_format_default(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        content.pop('prefix', None)  # remove prefix
        expected = {'entity': {'ex:ent': {'voprov:id': 'ex:ent', 'voprov:name': 'An example entity'}}}
        self.assertEqual(content, expected)

    def test_get_format_default2(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent', HTTP_ACCEPT="*/*")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        content.pop('prefix', None)  # remove prefix
        expected = {'entity': {'ex:ent': {'voprov:id': 'ex:ent', 'voprov:name': 'An example entity'}}}
        self.assertEqual(content, expected)

    def test_get_format_provn1(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent&RESPONSEFORMAT=PROV-N', HTTP_ACCEPT="*/*")
        self.assertEqual(response.status_code, 200)

    def test_get_format_provn2(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent&RESPONSEFORMAT=PROV-N', HTTP_ACCEPT="text/*")
        self.assertEqual(response.status_code, 200)

    def test_get_format_provn3(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent&RESPONSEFORMAT=PROV-N', HTTP_ACCEPT="text/plain")
        self.assertEqual(response.status_code, 200)

    def test_get_format_provn_wrongaccept(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent&RESPONSEFORMAT=PROV-N', HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 406)

    def test_get_format_provjson1(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent&RESPONSEFORMAT=PROV-JSON', HTTP_ACCEPT="*/*")
        self.assertEqual(response.status_code, 200)

    def test_get_format_provjson2(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent&RESPONSEFORMAT=PROV-JSON', HTTP_ACCEPT="application/*")
        self.assertEqual(response.status_code, 200)

    def test_get_format_provjson3(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent&RESPONSEFORMAT=PROV-JSON', HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 200)

    def test_get_format_provjson_wrongaccept(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent&RESPONSEFORMAT=PROV-JSON', HTTP_ACCEPT="text/plain")
        self.assertEqual(response.status_code, 406)

    def test_get_format_unsupported(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent&RESPONSEFORMAT=HUBBA')
        self.assertEqual(response.status_code, 415)

    def test_get_format_unsupportedaccept(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent', HTTP_ACCEPT="image/png")
        self.assertEqual(response.status_code, 415)


class ProvDAL_General_TestCase(TestCase):

    def setUp(self):
        a = Activity.objects.create(id="rave:act", name="myactivity")
        a.save()
        af = ActivityFlow.objects.create(id="rave:flow", name="myflow")
        af.save()
        h = HadStep.objects.create(activityFlow=af, activity=a)
        h.save()

        e = Entity.objects.create(id="rave:dr4", name="RAVE DR4")
        e.save()
        e0 = Entity.objects.create(id="rave:obs", name="RAVE observations")
        e0.save()

        wg = WasGeneratedBy.objects.create(entity=e, activity=a)
        wg.save()

        u = Used.objects.create(activity=a, entity=e0)
        u.save()

        #wd = WasDerivedFrom.objects.create(generatedEntity=e, usedEntity=e0)
        #wd.save()

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
        response = client.get(reverse('prov_vo:provdal')+'?ID=blabla&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        numlines = len(found)
        self.assertEqual(numlines, 0)

    def test_get_caseinsensitive(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?id=rave:obs&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""entity(rave:obs, [voprov:name="RAVE observations"])
"""
        self.assertEqual(content, expected)

    def test_get_caseinsensitive_multi(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?id=rave:obs&ID=rave:dr4&RESPONSEFORMAT=PROV-N&DEPTH=0')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""entity(rave:dr4, [voprov:name="RAVE DR4"])
entity(rave:obs, [voprov:name="RAVE observations"])
"""
        self.assertEqual(content, expected)

    def test_get_multisinglevalues(self):
        client = Client()
        for param in ['FORMAT', 'DEPTH', 'MODEL', 'MEMBERS', 'STEPS', 'AGENT', 'DIRECTION']:
            response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&%s=1&%s=2' % (param, param))
            self.assertEqual(response.status_code, 400)
            content = response.content
            expected = "Bad request: parameter %s must occur only once or not at all." % (param)
        self.assertEqual(content, expected)

    def test_get_unsupportedparameter(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&SOMETHING=nothing')
        self.assertEqual(response.status_code, 400)
        content = response.content
        expected = "Bad request: parameter SOMETHING is not supported by this service."
        self.assertEqual(content, expected)

    def test_get_unsupportedparameters(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&SOMETHING=nothing&ANYTHING=null')
        self.assertEqual(response.status_code, 400)
        content = response.content
        expected = "Bad request: parameters ANYTHING, SOMETHING are not supported by this service."
        self.assertEqual(content, expected)

    def test_getProvdalActivityID(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:act&DEPTH=0&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = """activity(rave:act, -, -, [voprov:name="myactivity"])\n"""
        self.assertEqual(expected, content)

    def test_getProvdalEntityID(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&DEPTH=0&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = """entity(rave:dr4, [voprov:name="RAVE DR4"])\n"""
        self.assertEqual(expected, content)

    def test_getProvdalAgentID(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=org:rave&DEPTH=1&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        # only the agent itself should be returned
        content = get_content(response)
        expected = """agent(org:rave, [voprov:name="RAVE project"])\n"""
        self.assertEqual(expected, content)

    def test_getProvdalEntityIDMultiple(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&ID=rave:obs&DEPTH=0&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = """entity(rave:dr4, [voprov:name="RAVE DR4"])
entity(rave:obs, [voprov:name="RAVE observations"])
"""
        self.assertEqual(expected, content)

    def test_getProvdalMixedIDs(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&ID=rave:act&ID=org:rave&DEPTH=0&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = """\
activity(rave:act, -, -, [voprov:name="myactivity"])
entity(rave:dr4, [voprov:name="RAVE DR4"])
agent(org:rave, [voprov:name="RAVE project"])
"""
        self.assertEqual(expected, content)

    def test_getProvdalActivityFlow(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        expected = 'activityFlow(rave:flow, -, -, [voprov:name="myflow"])'
        found = re.search(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(found.group(0), expected)

    def test_getProvdalActivityFlowDepth2(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow&DEPTH=2&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 1)

    def test_getProvdalActivityFlowIncludeSteps(self):
        # If STEPS=TRUE, substeps of the activityFlow shall be followed,
        # thus both, activityFlow and activity must be returned
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow&DEPTH=3&STEPS=true&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 2)

    def test_getProvdalActivityDepth2(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:act&DEPTH=2&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 2)

    # In this implementation, ID can also take an agent's ID, but agent relations are only
    # followed beyond the agent if AGENT option is set to TRUE
    def test_getProvdalAgentFollow(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=org:rave&AGENT=TRUE&DEPTH=1&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        # agent, activity, entity, wat and was. relation should be returned
        # strip begin/end document and prefix from response content:
        content = get_content(response)
        expected = \
"""activity(rave:act, -, -, [voprov:name="myactivity"])
entity(rave:dr4, [voprov:name="RAVE DR4"])
agent(org:rave, [voprov:name="RAVE project"])
wasAssociatedWith(rave:act, org:rave, -)
wasAttributedTo(rave:dr4, org:rave)
"""
        self.assertEqual(expected, content)

    def test_getProvdalBack(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:act&DEPTH=1&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = re.sub(r'document.*\n', '', response.content)
        content = re.sub(r'endDocument', '', content)
        content = re.sub(r'prefix.*\n', '', content)
        expected = \
"""activity(rave:act, -, -, [voprov:name="myactivity"])
activityFlow(rave:flow, -, -, [voprov:name="myflow"])
entity(rave:obs, [voprov:name="RAVE observations"])
agent(org:rave, [voprov:name="RAVE project"])
used(rave:act, rave:obs, -)
wasAssociatedWith(rave:act, org:rave, -)
hadStep(rave:flow, rave:act)
"""
        self.assertEqual(content, expected)

    def test_getProvdalForth(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:act&DEPTH=1&DIRECTION=FORTH&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = re.sub(r'document.*\n', '', response.content)
        content = re.sub(r'endDocument', '', content)
        content = re.sub(r'prefix.*\n', '', content)
        expected = \
"""activity(rave:act, -, -, [voprov:name="myactivity"])
activityFlow(rave:flow, -, -, [voprov:name="myflow"])
entity(rave:dr4, [voprov:name="RAVE DR4"])
agent(org:rave, [voprov:name="RAVE project"])
wasGeneratedBy(rave:dr4, rave:act, -)
wasAssociatedWith(rave:act, org:rave, -)
hadStep(rave:flow, rave:act)
"""
        self.assertEqual(content, expected)


class ProvDAL_Derivation_TestCase(TestCase):

    def setUp(self):
        e = Entity.objects.create(id="rave:dr4", name="RAVE DR4")
        e.save()
        e0 = Entity.objects.create(id="rave:obs", name="RAVE observations")
        e0.save()

        wd = WasDerivedFrom.objects.create(generatedEntity=e, usedEntity=e0)
        wd.save()

    def test_getProvdalBackDerivation(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&DEPTH=1&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""entity(rave:dr4, [voprov:name="RAVE DR4"])
entity(rave:obs, [voprov:name="RAVE observations"])
wasDerivedFrom(rave:dr4, rave:obs, -, -, -)
"""
        self.assertEqual(content, expected)

    def test_getProvdalForthDerivation(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:obs&DEPTH=1&DIRECTION=FORTH&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""entity(rave:obs, [voprov:name="RAVE observations"])
entity(rave:dr4, [voprov:name="RAVE DR4"])
wasDerivedFrom(rave:dr4, rave:obs, -, -, -)
"""
        self.assertEqual(content, expected)


class ProvDAL_Information_TestCase(TestCase):

    def setUp(self):
        a1 = Activity.objects.create(id="ex:act1", name="Activity 1")
        a1.save()
        a2 = Activity.objects.create(id="ex:act2", name="Activity 2")
        a2.save()

        wd = WasInformedBy.objects.create(informed=a2, informant=a1)
        wd.save()

    def test_getProvdalBackInformation(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:act2&DEPTH=1&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(ex:act1, -, -, [voprov:name="Activity 1"])
activity(ex:act2, -, -, [voprov:name="Activity 2"])
wasInformedBy(ex:act2, ex:act1)
"""
        self.assertEqual(content, expected)

    def test_getProvdalForthInformation(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:act1&DEPTH=1&DIRECTION=FORTH&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = re.sub(r'document.*\n', '', response.content)
        content = re.sub(r'endDocument', '', content)
        content = re.sub(r'prefix.*\n', '', content)
        expected = \
"""activity(ex:act1, -, -, [voprov:name="Activity 1"])
activity(ex:act2, -, -, [voprov:name="Activity 2"])
wasInformedBy(ex:act2, ex:act1)
"""
        self.assertEqual(content, expected)
