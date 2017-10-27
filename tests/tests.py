import datetime
import re
import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.test import TestCase

from django.test import Client
from django.test.utils import setup_test_environment

from prov_vo.models import Activity, ActivityFlow, HadStep
from prov_vo.models import Entity, Collection, WasGeneratedBy, Used, WasDerivedFrom, WasInformedBy, HadMember
from prov_vo.models import Agent, WasAssociatedWith, WasAttributedTo
from prov_vo.models import Parameter, ParameterDescription
from prov_vo.models import ActivityDescription, EntityDescription

from prov_vo.forms import ProvDalForm


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

    def test_getProvdalActivityFlowW3C(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow&RESPONSEFORMAT=PROV-N&MODEL=W3C')
        self.assertEqual(response.status_code, 200)
        expected = 'activity(rave:flow, -, -, [prov:label="myflow", voprov:votype="voprov:activityFlow"])'
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

    def test_getProvdalActivityFlowIncludeStepsW3C(self):
        # If STEPS=TRUE, substeps of the activityFlow shall be followed,
        # thus both, activityFlow and activity must be returned
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:flow&DEPTH=3&STEPS=true&RESPONSEFORMAT=PROV-N&MODEL=W3C')
        #print 'content: ', response.content
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^act.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 2)

        found2 = re.findall(r"^wasInfluencedBy.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found2), 1)

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


class ProvDAL_Generation_TestCase(TestCase):

    def setUp(self):
        a = Activity.objects.create(id="rave:act", name="myactivity")
        a.save()
        af = ActivityFlow.objects.create(id="rave:flow", name="myflow")
        af.save()
        h = HadStep.objects.create(activityFlow=af, activity=a)
        h.save()

        e = Entity.objects.create(id="rave:dr4", name="RAVE DR4")
        e.save()

        wg = WasGeneratedBy.objects.create(entity=e, activity=a)
        wg.save()

    def test_getProvdalBackGeneration(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&DEPTH=1&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(rave:act, -, -, [voprov:name="myactivity"])
entity(rave:dr4, [voprov:name="RAVE DR4"])
wasGeneratedBy(rave:dr4, rave:act, -)
"""
        self.assertEqual(content, expected)

    def test_getProvdalForthGeneration(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:act&DEPTH=1&DIRECTION=FORTH&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(rave:act, -, -, [voprov:name="myactivity"])
activityFlow(rave:flow, -, -, [voprov:name="myflow"])
entity(rave:dr4, [voprov:name="RAVE DR4"])
wasGeneratedBy(rave:dr4, rave:act, -)
hadStep(rave:flow, rave:act)
"""
        self.assertEqual(content, expected)


class ProvDAL_Usage_TestCase(TestCase):

    def setUp(self):
        a = Activity.objects.create(id="rave:act", name="myactivity")
        a.save()

        e = Entity.objects.create(id="rave:dr4", name="RAVE DR4")
        e.save()

        u = Used.objects.create(activity=a, entity=e)
        u.save()

    def test_getProvdalBackUsage(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:act&DEPTH=1&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(rave:act, -, -, [voprov:name="myactivity"])
entity(rave:dr4, [voprov:name="RAVE DR4"])
used(rave:act, rave:dr4, -)
"""
        self.assertEqual(content, expected)

    def test_getProvdalForthUsage(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&DEPTH=1&DIRECTION=FORTH&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(rave:act, -, -, [voprov:name="myactivity"])
entity(rave:dr4, [voprov:name="RAVE DR4"])
used(rave:act, rave:dr4, -)
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
        content = get_content(response)
        expected = \
"""activity(ex:act1, -, -, [voprov:name="Activity 1"])
activity(ex:act2, -, -, [voprov:name="Activity 2"])
wasInformedBy(ex:act2, ex:act1)
"""
        self.assertEqual(content, expected)


class ProvDAL_Membership_TestCase(TestCase):

    def setUp(self):
        c = Collection.objects.create(id="rave:dr4", name="RAVE DR4")
        c.save()
        e = Entity.objects.create(id="rave:stellar_properties", name="RAVE stellar properties")
        e.save()

        hm = HadMember.objects.create(collection=c, entity=e)
        hm.save()

    def test_getProvdalEntity(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:stellar_properties&DEPTH=1&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^entity.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 2)

    def test_getProvdalCollection(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&DEPTH=1&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^entity.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 1)

    def test_getProvdalCollectionIncludeMembers(self):
        # If MEMBERS=TRUE, members of a collection shall be followed,
        # thus both, collection and entity must be returned
        # (both serialized as "entity", so far)
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=rave:dr4&DEPTH=1&MEMBERS=true&RESPONSEFORMAT=PROV-N')
        self.assertEqual(response.status_code, 200)
        found = re.findall(r"^entity.*", response.content, flags=re.MULTILINE)
        self.assertEqual(len(found), 2)


class ProvDAL_Parameter_TestCase(TestCase):

    def setUp(self):
        a = Activity.objects.create(id="ex:act", name="myactivity")
        a.save()
        pd = ParameterDescription.objects.create(id="ex:paramdesc1", name="Parameter1", unit="sec", datatype="float")
        pd.save()
        p = Parameter.objects.create(id="ex:param1", activity=a, value="1.0", description=pd)
        p.save()

    def test_getProvdalParameterProvN(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:act&DEPTH=1&RESPONSEFORMAT=PROV-N&MODEL=IVOA')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(ex:act, -, -, [voprov:name="myactivity"])
parameter(ex:param1, ex:act, 1.0, [voprov:description="ex:paramdesc1"])
parameterDescription(ex:paramdesc1, Parameter1, [voprov:datatype="float", voprov:unit="sec"])
"""
        self.assertEqual(content, expected)

    def test_getProvdalParameterProvJSON(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:act&DEPTH=1&RESPONSEFORMAT=PROV-JSON&MODEL=IVOA')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['activity'],
            {'ex:act': {'voprov:id': 'ex:act', 'voprov:name': 'myactivity'}})
        self.assertEqual(content['parameter'],
            {'ex:param1': {'voprov:activity': 'ex:act', 'voprov:description': 'ex:paramdesc1' , 'voprov:id': 'ex:param1', 'voprov:value': '1.0'}
            })
        self.assertEqual(content['parameterDescription'],
            {u'ex:paramdesc1': {u'voprov:id': u'ex:paramdesc1', u'voprov:unit': u'sec',
            u'voprov:name': u'Parameter1', u'voprov:datatype': u'float'}}
            )
    def test_getProvdalParameterProvNW3C(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:act&DEPTH=1&RESPONSEFORMAT=PROV-N&MODEL=W3C')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(ex:act, -, -, [prov:label="myactivity"])
entity(ex:param1, [prov:value="1.0", prov:label="Parameter1", voprov:votype="voprov:parameter", voprov:activity="ex:act", voprov:datatype="float", voprov:unit="sec"])
"""
        self.assertEqual(content, expected)


class ProvDAL_ActivityDescription_TestCase(TestCase):

    def setUp(self):
        ad = ActivityDescription.objects.create(id="ex:actdesc1", name="Activity Description 1", type="observation")
        ad.save()
        a = Activity.objects.create(id="ex:act1", name="Activity 1", description=ad)
        a.save()

    def test_getProvdalActivityDescriptionProvN(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:act1&DEPTH=1&RESPONSEFORMAT=PROV-N&MODEL=IVOA')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(ex:act1, -, -, [voprov:name="Activity 1", voprov:description="ex:actdesc1"])
activityDescription(ex:actdesc1, Activity Description 1, [voprov:type="observation"])
"""
        self.assertEqual(content, expected)

    def test_getProvdalActivityDescriptionProvJSON(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:act1&DEPTH=1&RESPONSEFORMAT=PROV-JSON&MODEL=IVOA')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['activity'],
            {'ex:act1': {'voprov:id': 'ex:act1', 'voprov:name': 'Activity 1', 'voprov:description': 'ex:actdesc1'}})
        self.assertEqual(content['activityDescription'],
            {'ex:actdesc1': {'voprov:id': 'ex:actdesc1', 'voprov:name': 'Activity Description 1', 'voprov:type': 'observation'}
            })

    def test_getProvdalActivityDescriptionProvNW3C(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:act1&DEPTH=1&RESPONSEFORMAT=PROV-N&MODEL=W3C')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(ex:act1, -, -, [prov:label="Activity 1", voprov:description="ex:actdesc1"])
entity(ex:actdesc1, [prov:label="Activity Description 1", voprov:votype="voprov:activityDescription", prov:type="observation"])
"""
        self.assertEqual(content, expected)


class ProvDAL_EntityDescription_TestCase(TestCase):

    def setUp(self):
        ed = EntityDescription.objects.create(id="ex:entdesc1", name="Entity Description 1", category="image")
        ed.save()
        e = Entity.objects.create(id="ex:ent1", name="Entity 1", description=ed)
        e.save()

    def test_getProvdalEntityDescriptionProvN(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent1&DEPTH=1&RESPONSEFORMAT=PROV-N&MODEL=IVOA')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""entity(ex:ent1, [voprov:name="Entity 1", voprov:description="ex:entdesc1"])
entityDescription(ex:entdesc1, Entity Description 1, [voprov:category="image"])
"""
        self.assertEqual(content, expected)

    def test_getProvdalEntityDescriptionProvJSON(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent1&DEPTH=1&RESPONSEFORMAT=PROV-JSON&MODEL=IVOA')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content['entity'],
            {'ex:ent1': {'voprov:id': 'ex:ent1', 'voprov:name': 'Entity 1', 'voprov:description': 'ex:entdesc1'}})
        self.assertEqual(content['entityDescription'],
            {'ex:entdesc1': {'voprov:id': 'ex:entdesc1', 'voprov:name': 'Entity Description 1', 'voprov:category': 'image'}
            })

    def test_getProvdalEntityDescriptionProvNW3C(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal')+'?ID=ex:ent1&DEPTH=1&RESPONSEFORMAT=PROV-N&MODEL=W3C')
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""entity(ex:entdesc1, [prov:label="Entity Description 1", voprov:votype="voprov:entityDescription", voprov:category="image"])
entity(ex:ent1, [prov:label="Entity 1", voprov:description="ex:entdesc1"])
"""
        self.assertEqual(content, expected)


class ProvDAL_Graph_TestCase(TestCase):

    def setUp(self):
        e = Entity.objects.create(id="rave:dr4", name="RAVE DR4")
        e.save()
        e0 = Entity.objects.create(id="rave:obs", name="RAVE observations")
        e0.save()

        wd = WasDerivedFrom.objects.create(generatedEntity=e, usedEntity=e0)
        wd.save()

        #self.client = Client()

    def test_getProvdalGraph(self):
        client = Client()
        url = reverse('prov_vo:provdal')+'?ID=rave:dr4&DEPTH=1&RESPONSEFORMAT=GRAPH'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prov_vo/provdal_graph.html')

    def test_getProvdalGraphJson(self):
        client = Client()
        url = reverse('prov_vo:provdal')+'?ID=rave:dr4&DEPTH=1&RESPONSEFORMAT=GRAPH-JSON'
        response = client.get(url)
        self.assertEqual(response.status_code, 200)

        expected = \
"""{"nodes": [{"type": "entity", "name": "RAVE DR4"}, {"type": "entity", "name": "RAVE observations"}],""" + \
""" "links": [{"source": 0, "type": "wasDerivedFrom", "target": 1, "value": 0.2}]}"""
        self.assertEqual(response.content, expected)


class ProvDALForm_TestCase(TestCase):

    def setUp(self):
        e = Entity.objects.create(id="rave:dr4", name="RAVE DR4")
        e.save()

    def test_provdalform_settings(self):
        client = Client()
        response = client.get(reverse('prov_vo:provdal_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prov_vo/provdalform.html')

    # Test what happens, if PROV_VO_CONFIG does not contain 'provdalform' keyword:
    # TODO: => test does not work, because for some reason in forms.py the
    #       original settings are imported (but in views it's the custom ones ...)
    # def test_provdalform_settingsfail(self):
    #     client = Client()
    #     with self.settings(PROV_VO_CONFIG = {'notprovdal': {'foo': 'bar'}}):
    #         response = client.get(reverse('prov_vo:provdal_form'))
    #         self.assertEqual(response.status_code, 200)
    #         self.assertTemplateUsed(response, 'prov_vo/provdalform.html')

    def test_provdalform(self):
        form_data = {'obj_id': 'rave:dr4'}
        form = ProvDalForm(form_data)
        self.assertTrue(form.is_valid())

    def test_provdalform_invalid(self):
        form_data = {}
        form = ProvDalForm(form_data)
        self.assertFalse(form.is_valid())

    def test_provdalform_postempty(self):
        client = Client()
        response = client.post(reverse('prov_vo:provdal_form'))
        # if no data were submitted, just display the form again:
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'obj_id', 'This field is required.')
        self.assertTemplateUsed(response, 'prov_vo/provdalform.html')

    def test_provdalform_post(self):
        client = Client()
        response = client.post(reverse('prov_vo:provdal_form'),
            {'obj_id': 'rave:dr4', 'depth': '1', 'direction': 'BACK', 'format': 'PROV-JSON', 'model': 'IVOA'})
        # should redirect to provdal:
        self.assertEqual(response.status_code, 302)

        url = '/prov_vo/provdal/?ID=rave:dr4&DEPTH=1&DIRECTION=BACK&MEMBERS=FALSE&STEPS=FALSE&AGENT=FALSE&RESPONSEFORMAT=PROV-JSON&MODEL=IVOA'
        self.assertEqual(response.url, url)

class View_Allprov_TestCase(TestCase):
    def setUp(self):
        e = Entity.objects.create(id="ex:ent1", name="Entity 1")
        e.save()

        a1 = Activity.objects.create(id="ex:act1", name="Activity 1")
        a1.save()

        a2 = Activity.objects.create(id="ex:act2", name="Activity 2")
        a2.save()

    def test_allprov_provn(self):
        client = Client()
        response = client.get(reverse('prov_vo:allprov', kwargs={'format':'PROV-N'}))
        self.assertEqual(response.status_code, 200)
        content = get_content(response)
        expected = \
"""activity(ex:act1, -, -, [prov:label="Activity 1"])
activity(ex:act2, -, -, [prov:label="Activity 2"])
entity(ex:ent1, [prov:label="Entity 1"])
"""
        self.assertEqual(content, expected)

    def test_allprov_provjson(self):
        client = Client()
        response = client.get(reverse('prov_vo:allprov', kwargs={'format':'PROV-JSON'}))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)

        self.assertEqual(content['activity'],
            {'ex:act1': {'prov:id': 'ex:act1', 'prov:label': 'Activity 1'},
             'ex:act2': {'prov:id': 'ex:act2', 'prov:label': 'Activity 2'}
            })
        self.assertEqual(content['entity'],
            {'ex:ent1': {'prov:id': 'ex:ent1', 'prov:label': 'Entity 1'}
            })
