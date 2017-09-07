import sys # just for debugging
import json
from datetime import datetime

from django.conf import settings

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
#from django.template import loader
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.views import generic
from django.http import JsonResponse
from django.db.models.fields.related import ManyToManyField
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict
from django.utils.datastructures import MultiValueDict

from braces.views import JSONResponseMixin

#from rest_framework.renderers import XMLRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import viewsets

import utils

from .models import (
    Activity,
    Entity,
    Agent,
    Used,
    WasGeneratedBy,
    WasAssociatedWith,
    WasAttributedTo,
    HadMember,
    HadStep,
    WasDerivedFrom,
    WasInformedBy,
    ActivityFlow,
    Collection
    #Bundle,
)

from .serializers import (
    ActivitySerializer,
    EntitySerializer,
    AgentSerializer,
    UsedSerializer,
    WasGeneratedBySerializer,
    WasAssociatedWithSerializer,
    WasAttributedToSerializer,
    HadMemberSerializer,
    WasDerivedFromSerializer,
    WasInformedBySerializer,
    W3CCollectionSerializer,
    W3CProvenanceSerializer,
    VOProvenanceSerializer,
    ProvenanceGraphSerializer
)

from .renderers import PROVNRenderer, PROVJSONRenderer

from .forms import ProvDalForm


class IndexView(generic.TemplateView):
    template_name = 'prov_vo/index.html'

class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    queryset = Activity.objects.all()

class EntityViewSet(viewsets.ModelViewSet):
    serializer_class = EntitySerializer
    queryset = Entity.objects.all()

class AgentViewSet(viewsets.ModelViewSet):
    serializer_class = AgentSerializer
    queryset = Agent.objects.all()

class UsedViewSet(viewsets.ModelViewSet):
    serializer_class = UsedSerializer
    queryset = Used.objects.all()

class WasGeneratedByViewSet(viewsets.ModelViewSet):
    serializer_class = WasGeneratedBySerializer
    queryset = WasGeneratedBy.objects.all()

class WasAssociatedWithViewSet(viewsets.ModelViewSet):
    serializer_class = WasAssociatedWithSerializer
    queryset = WasAssociatedWith.objects.all()

class WasAttributedToViewSet(viewsets.ModelViewSet):
    serializer_class = WasAttributedToSerializer
    queryset = WasAttributedTo.objects.all()

class HadMemberViewSet(viewsets.ModelViewSet):
    serializer_class = HadMemberSerializer
    queryset = HadMember.objects.all()

class WasDerivedFromViewSet(viewsets.ModelViewSet):
    serializer_class = WasDerivedFromSerializer
    queryset = WasDerivedFrom.objects.all()

# class ActivityFlowViewSet(viewsets.ModelViewSet):
#     serializer_class = ActivityFlowSerializer
#     queryset = ActivityFlow.objects.all()

class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = W3CCollectionSerializer
    queryset = Collection.objects.all()


def convert_to_dict_querysets(listqueryset):

    objdict = {}
    for q in listqueryset:
        objdict[q.id] = q

    return objdict


# simple prov-n view of everything
def allprov(request, format):

    # first store everything in a prov-dictionary
    prefix = {
        "voprov": "http://www.ivoa.net/documents/ProvenanceDM/voprov/",
        "org": "http://www.ivoa.net/documents/ProvenanceDM/voprov/org/",
        "vo": "http://www.ivoa.net/documents/ProvenanceDM/voprov/vo",
        "prov": "http://www.w3.org/ns/prov#",  # defined by default
        "xsd": "http://www.w3.org/2000/10/XMLSchema#"  # defined by default
    }

    # add prefixes from settings:
    if settings.PROV_VO_CONFIG.namespaces:
        for key, value in settings.PROV_VO_CONFIG.namespaces.items():
            prefix[key] = value


    prov = {
        'prefix': prefix,
        'activity': convert_to_dict_querysets(Activity.objects.all()),
        'activityFlow': convert_to_dict_querysets(ActivityFlow.objects.all()),
        'entity': convert_to_dict_querysets(Entity.objects.all()),
        'collection': convert_to_dict_querysets(Collection.objects.all()),
        'agent': convert_to_dict_querysets(Agent.objects.all()),
        'used': convert_to_dict_querysets(Used.objects.all()),
        'wasGeneratedBy': convert_to_dict_querysets(WasGeneratedBy.objects.all()),
        'wasAssociatedWith': convert_to_dict_querysets(WasAssociatedWith.objects.all()),
        'wasAttributedTo': convert_to_dict_querysets(WasAttributedTo.objects.all()),
        'hadMember': convert_to_dict_querysets(HadMember.objects.all()),
        'wasDerivedFrom': convert_to_dict_querysets(WasDerivedFrom.objects.all()),
        'hadStep': convert_to_dict_querysets(HadStep.objects.all()),
        'wasInformedBy': convert_to_dict_querysets(WasInformedBy.objects.all())
    }

    # serialize it (W3C):
    serializer = W3CProvenanceSerializer(prov)
    data = serializer.data

    # write provenance information in desired format:
    if format == 'PROV-N':
        provstr = PROVNRenderer().render(data)
        return HttpResponse(provstr, content_type='text/plain; charset=utf-8')

    elif format == 'PROV-JSON':
        json_str = PROVJSONRenderer().render(data)
        return HttpResponse(json_str, content_type='application/json; charset=utf-8')

    else:
        # format is not known, return error
        provstr = "Sorry, unknown format %s was requested, cannot handle this." % format

    return HttpResponse(provstr, content_type='text/plain; charset=utf-8')


def prettyprovn(request):
    # use hyperlinks for ids
    # still missing new classes, just used for testing
    activity_list = Activity.objects.order_by('-startTime')[:]
    entity_list = Entity.objects.order_by('-name')[:]
    agent_list = Agent.objects.order_by('-name')[:]
    used_list = Used.objects.order_by('-id')[:]
    wasGeneratedBy_list = WasGeneratedBy.objects.order_by('-id')[:]
    wasAssociatedWith_list = WasAssociatedWith.objects.order_by('-id')[:]
    wasAttributedTo_list = WasAttributedTo.objects.order_by('-id')[:]

    return render(request, 'prov_vo/provn.html',
                 {'activity_list': activity_list,
                  'entity_list': entity_list,
                  'agent_list': agent_list,
                  'used_list': used_list,
                  'wasGeneratedBy_list': wasGeneratedBy_list,
                  'wasAssociatedWith_list': wasAssociatedWith_list,
                  'wasAttributedTo_list': wasAttributedTo_list
                 })


def graph(request):
    return render(request, 'prov_vo/graph.html', {'url': 'graphjson'})


def fullgraphjson(request):
    # TODO: should construct this similar to provdal-version

    activity_list = Activity.objects.all()
    entity_list = Entity.objects.all()
    agent_list = Agent.objects.all()

    used_list = Used.objects.all()
    wasGeneratedBy_list = WasGeneratedBy.objects.all()
    wasAssociatedWith_list = WasAssociatedWith.objects.all()
    wasAttributedTo_list = WasAttributedTo.objects.all()
    hadMember_list = HadMember.objects.all()

    nodes_dict = []
    count_nodes = 0
    count_act = 0

    links_dict = []
    count_link = 0

    map_activity_ids = {}
    map_entity_ids = {}
    map_agent_ids = {}


    for a in activity_list:
        nodes_dict.append({"name": a.name, "type": "activity"})
        map_activity_ids[a.id] = count_nodes
        count_nodes = count_nodes + 1

    for e in entity_list:
        nodes_dict.append({"name": e.name, "type": "entity"})
        map_entity_ids[e.id] = count_nodes
        count_nodes = count_nodes + 1

    for ag in agent_list:
        nodes_dict.append({"name": ag.name, "type": "agent"})
        map_agent_ids[ag.id] = count_nodes
        count_nodes = count_nodes + 1

    # add links (source, target, value)
    for u in used_list:
        links_dict.append({"source": map_activity_ids[u.activity.id], "target": map_entity_ids[u.entity.id], "value": 0.5, "type": "used"})
        count_link = count_link + 1

    for w in wasGeneratedBy_list:
        links_dict.append({"source": map_entity_ids[w.entity.id], "target": map_activity_ids[w.activity.id], "value": 0.5, "type": "wasGeneratedBy"})
        count_link = count_link + 1

    for w in wasAssociatedWith_list:
        links_dict.append({"source": map_activity_ids[w.activity.id], "target": map_agent_ids[w.agent.id], "value": 0.2, "type": "wasAssociatedWith"})
        count_link = count_link + 1

    for w in wasAttributedTo_list:
        links_dict.append({"source": map_entity_ids[w.entity.id], "target": map_agent_ids[w.agent.id], "value": 0.2, "type": "wasAttributedTo"})
        count_link = count_link + 1

    for h in hadMember_list:
        s =  map_entity_ids[h.collection_id]
        #print >>sys.stderr, 'h.collection_id, h.entity_id: ', h.collection_id, ", '"+h.entity_id+"'"
        t = map_entity_ids[h.entity_id]
        #print "map_entity_ids[h.collection_id]"
        #links_dict.append({"source": map_entity_ids[h.collection_id], "target": map_entity_ids[h.entity_id], "value": 0.2, "type": "hadMember"})
        links_dict.append({"source": s, "target": t, "value": 0.2, "type": "hadMember"})
        count_link = count_link + 1


    prov_dict = {"nodes": nodes_dict, "links": links_dict}

    return JsonResponse(prov_dict)



def provdal_form(request):

    if request.method == 'POST':
        form = ProvDalForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
        # process the data in form.cleaned_data as required
            try:
                obj_id = form.cleaned_data['obj_id']
                depth = form.cleaned_data['depth']
                direction = form.cleaned_data['direction']
                members = form.cleaned_data['members']
                steps = form.cleaned_data['steps']
                agent = form.cleaned_data['agent']
                format = form.cleaned_data['format']
                compliance = form.cleaned_data['model']

                return HttpResponseRedirect(
                    reverse('prov_vo:provdal')+"?ID=%s&DEPTH=%s&DIRECTION=%s&MEMBERS=%s&STEPS=%s&AGENT=%s&FORMAT=%s&MODEL=%s" %
                    (str(obj_id), str(depth).upper(), str(direction).upper(), str(members).upper(),
                    str(steps).upper(), str(agent).upper(), str(format).upper(),
                    str(compliance).upper()))

            except ValueError:
                form = ProvDalForm(request.POST)
        else:
            #print form.errors # or add_error??
            pass

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ProvDalForm()

    return render(request, 'prov_vo/provdalform.html', {'form': form})

def get_urlparam(g, paramname, multi=False, required=False, default=None):
    if paramname in g:
        value = g[paramname]
        #print 'value: ', value
    else:
        if required == True:
            return None, HttpResponse('Bad request: the %s parameter is required.' % (paramname), status=400)
        else:
            return default, None  # even if default is None

    if len(value) == 1:
        if multi == False:
            return value[0], None
        else:
            return value, None
    else:
        if multi == False:
            return None, HttpResponse('Bad request: the %s parameter must occur only once or not at all.' % (paramname), status=400)
        else:
            return value, None

class QueryDictDALI(QueryDict):
    """
    Same as QueryDict class, but allows retrieval of URL parameter values
    with case-insensitive parameters as required by VO's DALI spec

    Example:
    QueryDict.get('ID') and QueryDict.get('id') should both return the same result.

    ... maybe that's not the problem.
    Actually, need to enforce single value if expecting single value
    And that required parameters exist.
    """

    def __init__(self, querydict=None):
        super(QueryDictDALI, self).__init__()
        self._mutable = True
        if querydict:

            # copy values
            for key, values in querydict.iterlists():
                self.setlist(key, values)

            # make it all upper case
            self.make_upper_case_parameter_names()


    def getsingle(self, key, default=None):
        """
        Return the data value for the passed key. If key doesn't exist
        or value is an empty list, return `default`.
        Ensure that the key occured only one single time, otherwise raise error
        """
        try:
            val = self.getlist(key)
        except KeyError:
            return default
        if val == []:
            return default
        if isinstance(val, list) and len(val) > 1:
            raise ValueError('Bad request: parameter %s should occur only once.' % key)

        return val[0]

    def make_upper_case_parameter_names(self):
        for key in self.keys():

            if key.upper() != key:
                values = self.getlist(key)

                if key.upper() in self:
                    oldvalues = self.getlist(key.upper())
                    self.setlist(key.upper(), oldvalues + values)
                else:
                    self.setlist(key.upper(), values)

                # delete this key entry
                self.pop(key)


def upper_case_params_querydict(querydict):
    updict = querydict.copy()

    for key in updict.keys():

        if key.upper() != key:
            values = updict.getlist(key)

            if key.upper() in updict:
                oldvalues = updict.getlist(key.upper())
                updict.setlist(key.upper(), oldvalues + values)
            else:
                updict.setlist(key.upper(), values)

            # delete this key entry
            updict.pop(key)

    return updict


def provdal(request):

    # Make a copy of request.GET dictionary and make all keys
    # upper case, because GET parameters need to be treated
    # case-insensitive according to DALI spec
    # (but not their values)

    h = QueryDictDALI(querydict=request.GET) #make a copy from req.GET right here?
    #h = upper_case_params_querydict(request.GET)

    # There can be more than one ID given, thus use getlist:
    if 'ID' not in h:
        return HttpResponse('Bad request: the ID parameter is required.', status=400)
    id_list = h.getlist('ID')

    try:
        depth = h.getsingle('DEPTH', default='1')
    except ValueError as e:
        return HttpResponse(e.message, status=400)

    try:
        direction = h.getsingle('DIRECTION', default='BACK')
    except ValueError as e:
        return HttpResponse(e.message, status=400)

    try:
        format = h.getsingle('FORMAT')  # set default after evaluating accept-header
    except ValueError as e:
        return HttpResponse(e.message, status=400)

    try:
        model = h.getsingle('MODEL', 'IVOA')  # one of IVOA, W3C (or None?)
    except ValueError as e:
        return HttpResponse(e.message, status=400)

    # new optional parameters
    try:
        members = request.GET.get('MEMBERS', 'FALSE')  # True for tracking members of collections
    except ValueError as e:
        return HttpResponse(e.message, status=400)
    try:
        steps = request.GET.get('STEPS', 'FALSE')   # True for tracking steps of activityFlows
    except ValueError as e:
        return HttpResponse(e.message, status=400)
    try:
        agent = request.GET.get('AGENT', 'FALSE')   # True for tracking all relations to/from agents
    except ValueError as e:
        return HttpResponse(e.message, status=400)

    #print 'meta: ', request.META
    if 'HTTP_ACCEPT' in request.META:
        http_accept = request.META['HTTP_ACCEPT']
    else:
        http_accept = "*/*"
    #if '*/*' in request.content_type:
    #    if format is None:
            # set a default:
    #        format = 'PROV-N'
    if format is None:
        # take format based on accept header
        if 'application/json' in http_accept:
            format = 'PROV-JSON'
        elif 'text/plain' in http_accept:
            format = 'PROV-N'
        # set some defaults:
        elif 'application/*' in http_accept:
            format = 'PROV-JSON'
        elif 'text/*' in http_accept:
            format = 'PROV-N'
        elif '*/*' in http_accept:
            # set a default format here:
            format = 'PROV-JSON'
        else:
            # 415 Unsupported media type
            responsestr = "Sorry, media type '%s' was requested, but is not supported by this service." % http_accept
            return HttpResponse(responsestr, status=415, content_type='text/plain; charset=utf-8')

    #print 'http_accept: ', http_accept
    if format not in "PROV-N PROV-JSON GRAPH GRAPH-JSON":
        # 415 Unsupported media type
        responsestr = "Sorry, format '%s' was requested, but is not supported by this service." % format
        return HttpResponse(responsestr, status=415, content_type='text/plain; charset=utf-8')

    # check for format and accept header compatibility
    if (format == 'PROV-N' and (
            http_accept.find('text/*') >= 0
            or http_accept.find("text/plain") >= 0
            or http_accept.find("*/*") >= 0)
        ):
        #print 'use PROV-N'
        pass
    elif (format == 'PROV-JSON' and (\
            http_accept.find('application/*') >= 0\
            or http_accept.find('application/json') >= 0\
            or http_accept.find('*/*') >= 0)\
        ):
        #print 'use PROV-JSON'
        pass
    elif (format == 'GRAPH' and (\
            http_accept.find('text/*') >= 0
            or http_accept.find("text/html") >= 0
            or http_accept.find("*/*") >= 0)
        ):
        #print 'use GRAPH'
        pass
    elif (format == 'GRAPH-JSON' and (\
            http_accept.find('text/*') >= 0
            or http_accept.find("text/html") >= 0
            or http_accept.find("*/*") >= 0)
        ):
        #print 'use GRAPH'
        pass
    else:
        #print "Need to complain"
        # return 406 Not Acceptable
        responsestr = "Sorry, format %s and media type %s were requested, but are not compatible." % (format, http_accept)
        return HttpResponse(responsestr, status=406, content_type='text/plain; charset=utf-8')


    if format == 'GRAPH':
        ids = ''
        for i in id_list:
            ids += 'ID=%s&' % i
        return render(request, 'prov_vo/provdal_graph.html',
            {'url': reverse('prov_vo:provdal') + "?%sDEPTH=%s&DIRECTION=%s&MEMBERS=%s&STEPS=%s&AGENT=%s&FORMAT=GRAPH-JSON&MODEL=%s" % (ids, str(depth), str(direction), str(members), str(steps), str(agent), str(model))})

    # check flags
    countdown = -1
    all_flag = False
    if str(depth).upper() == "ALL":
        # will search for all further provenance, recursively
        countdown = -1
        all_flag = True
    elif depth.isdigit():
        # follow at most backward relations along provenance history
        countdown = int(depth)
        all_flag = False
    else:
        # raise error: not supported
        raise ValidationError(
            'Invalid value: %(value)s is not supported',
            code='invalid',
            params={'value': depth},
        )

    # check optional parameter values
    members_flag = False
    steps_flag = False
    agent_flag = False

    if members.upper() == 'TRUE':
        members_flag = True
    if steps.upper() == 'TRUE':
        steps_flag = True
    if agent.upper() == 'TRUE':
        agent_flag = True

    prefix = {
        "voprov": "http://www.ivoa.net/documents/ProvenanceDM/voprov/",
        "org": "http://www.ivoa.net/documents/ProvenanceDM/voprov/org/",
        "vo": "http://www.ivoa.net/documents/ProvenanceDM/voprov/vo",
        "prov": "http://www.w3.org/ns/prov#",  # defined by default
        "xsd": "http://www.w3.org/2000/10/XMLSchema#"  # defined by default
    }

    # add (project specific) prefixes from (global) settings:
    if settings.PROV_VO_CONFIG['namespaces']:
        for key, value in settings.PROV_VO_CONFIG['namespaces'].items():
            prefix[key] = value

    prov = {
        'prefix': prefix,
        'activity': {},
        'activityFlow': {},
        'entity': {},
        'collection': {},  # not used, yet, stored with entities
        'agent': {},
        'used': {},
        'wasGeneratedBy': {},
        'wasAssociatedWith': {},
        'wasAttributedTo': {},
        'hadMember': {},
        'wasDerivedFrom': {},
        'hadStep': {},
        'wasInformedBy': {},
        'wasInfluencedBy': {}
    }

    # Note: even if collection class is used, Entity.objects.all() still contains all entities
    for obj_id in id_list:
        #print 'obj_id: ', obj_id
        try:
            entity = Entity.objects.get(id=obj_id)
            # store current entity in dict and search for provenance:
            prov['entity'][entity.id] = entity
            prov = utils.track_entity(entity, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)

        except Entity.DoesNotExist:
            pass
            # do not return, just continue with other ids
            # (and if none of them exists, return empty provenance record)

        try:
            activity = Activity.objects.get(id=obj_id)
            # or store current activity and search for its provenance
            activity_type = utils.get_activity_type(obj_id)

            prov[activity_type][activity.id] = activity
            prov = utils.track_activity(activity, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)
        except Activity.DoesNotExist:
            pass

        try:
            agent = Agent.objects.get(id=obj_id)
            prov['agent'][agent.id] = agent
            if agent_flag:
                prov = utils.track_agent(agent, prov, countdown,
                    all_flag=all_flag,
                    direction=direction,
                    members_flag=members_flag,
                    steps_flag=steps_flag,
                    agent_flag=agent_flag)
        except Agent.DoesNotExist:
            pass

    # The prov dictionary now contains the complete provenance information,
    # for all given entity ids,
    # in the form of a dictionary of querysets. First serialize them according to
    # the specified model.
    if model == "W3C":
        serializer = W3CProvenanceSerializer(prov)
    elif model == "IVOA":
        serializer = VOProvenanceSerializer(prov)
    else:
        # raise error: not supported
        raise ValidationError(
           'Invalid value: %(value)s is not supported',
            code='invalid',
            params={'value': model},
        )

    data = serializer.data

    # Render provenance information in desired format:
    if format == 'PROV-N':
        provstr = PROVNRenderer().render(data)
        return HttpResponse(provstr, content_type='text/plain; charset=utf-8')

    elif format == 'PROV-JSON':

        json_str = PROVJSONRenderer().render(data)
        return HttpResponse(json_str, content_type='application/json; charset=utf-8')

    elif format == "GRAPH-JSON":
        # need to re-structure the serialized data
        serializer = ProvenanceGraphSerializer(data, model=model)
        prov_dict = serializer.data
        return JsonResponse(prov_dict)

    else:
        # format is not known, return error
        # 415 Unsupported media type
        provstr = "Sorry, unknown format %s was requested, cannot handle this." % format
        return HttpResponse(provstr, status=415, content_type='text/plain; charset=utf-8')
