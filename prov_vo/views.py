import sys # just for debugging
import json
from datetime import datetime

from django.conf import settings

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError
from django.http import Http404
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
from utils import QueryDictDALI
from decorators import exceptions_to_http_status

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
from vosi.models import VOResource_Capability, Availability, AvailabilityOption

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
from vosi.renderers import VosiAvailabilityRenderer, VosiCapabilityRenderer

from .forms import ProvDalForm
#from vosi.views import availability, capabilities


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
    try:
        for key, value in settings.PROV_VO_CONFIG.namespaces.items():
            prefix[key] = value
    except AttributeError, e:
        pass


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
                    reverse('prov_vo:provdal')+"?ID=%s&DEPTH=%s&DIRECTION=%s&MEMBERS=%s&STEPS=%s&AGENT=%s&RESPONSEFORMAT=%s&MODEL=%s" %
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


@exceptions_to_http_status
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
    h.removekey('ID')
    depth = h.getsingle('DEPTH', default='1', removekey=True)
    direction = h.getsingle('DIRECTION', default='BACK', removekey=True)
    format = h.getsingle('RESPONSEFORMAT', default='PROV-JSON', removekey=True)  # set default after evaluating accept-header

    # optional parameters
    members_flag = h.getsingle('MEMBERS', default='FALSE', removekey=True)  # True for tracking members of collections
    steps_flag = h.getsingle('STEPS', default='FALSE', removekey=True)   # True for tracking steps of activityFlows
    agent_flag = h.getsingle('AGENT', default='FALSE', removekey=True)   # True for tracking all relations to/from agents

    # only in this implementation, not part of the standard
    model = h.getsingle('MODEL', default='IVOA', removekey=True)  # one of IVOA, W3C (or None?)

    # if there are any more (unexpected) parameters, throw an error
    if len(h.keys()) > 0:
        params = ', '.join(p for p in h.keys())
        if len(h.keys()) == 1:
            return HttpResponseBadRequest('Bad request: parameter %s is not supported by this service.' % params)
        else:
            return HttpResponseBadRequest('Bad request: parameters %s are not supported by this service.' % params)


    # check accept header and compare with RESPONSEFORMAT; if incompatible, then throw an error
    # default format is PROV-JSON (see standard specification, thus even if the RESPONSEFORMAT
    # is None, the http-accept must be compatible to the default format)
    errcode, errmsg = check_accept_header_reponseformat(request, format)
    if errcode is not None:
        return HttpResponse(errmsg, status=errcode, content_type='text/plain; charset=utf-8')

    if format == 'GRAPH':
        ids = ''
        for i in id_list:
            ids += 'ID=%s&' % i
        return render(request, 'prov_vo/provdal_graph.html',
            {'url': reverse('prov_vo:provdal') + "?%sDEPTH=%s&DIRECTION=%s&MEMBERS=%s&STEPS=%s&AGENT=%s&RESPONSEFORMAT=GRAPH-JSON&MODEL=%s" % (ids, str(depth), str(direction), str(members), str(steps), str(agent), str(model))})

    # check flags
    countdown = -1
    if str(depth).upper() == "ALL":
        # will search for all further provenance, recursively
        countdown = -1
    elif depth.isdigit():
        # follow at most this number of relations along provenance history
        countdown = int(depth)
    else:
        # raise error: not supported
        return HttpResponseBadRequest("Bad request: the value '%s' is not supported for parameter DEPTH" % (depth))


    # check optional parameter values
    members_flag = set_true_false('MEMBERS', members_flag)
    steps_flag = set_true_false('STEPS', steps_flag)
    agent_flag = set_true_false('AGENT', agent_flag)

    prefix = {
        "voprov": "http://www.ivoa.net/documents/ProvenanceDM/voprov/",
        "org": "http://www.ivoa.net/documents/ProvenanceDM/voprov/org/",
        "vo": "http://www.ivoa.net/documents/ProvenanceDM/voprov/vo",
        "prov": "http://www.w3.org/ns/prov#",  # defined by default
        "xsd": "http://www.w3.org/2000/10/XMLSchema#"  # defined by default
    }

    # add (project specific) prefixes from (global) settings:
    try:
        for key, value in settings.PROV_VO_CONFIG['namespaces'].items():
            prefix[key] = value
    except AttributeError, e:
        pass

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
        return HttpResponseBadRequest("Bad request: the value '%s' is not supported for parameter MODEL" % (model))

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


def check_accept_header_reponseformat(request, format):

    if 'HTTP_ACCEPT' in request.META:
        http_accept = request.META['HTTP_ACCEPT']
    else:
        http_accept = "*/*"


    if ("application/json" not in http_accept
        and "text/plain" not in http_accept
        and "application/*" not in http_accept
        and "text/*" not in http_accept
        and "*/*" not in http_accept):
        # 415 Unsupported media type
        responsestr = "Sorry, media type '%s' was requested, but is not supported by this service." % http_accept
        return 415, responsestr

    if format not in "PROV-N PROV-JSON GRAPH GRAPH-JSON":
        # 415 Unsupported media type
        responsestr = "Sorry, format '%s' was requested, but is not supported by this service." % format
        return 415, responsestr

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
        return 406, responsestr

    return None, None


def set_true_false(key, value):
    """
    Set the value for given key to True or False, depending on its value.
    Return error, if neither true nor false or equivalent are given.
    """

    if value.upper() == 'TRUE' or value == '1':
        value = True
    elif value.upper() == 'FALSE' or value == '0':
        value = False
    else:
        raise InvalidDataError("Bad request: the value '%s' is not supported for parameter %s" % (value, key))
    return value


# VOSI views
# ----------
# Can reuse the views from the vosi-package, as long as
# I don't need any custom changes. So no need to put
# any VOSI views here.
# def vosi_availability(request):
#    pass

# def vosi_capabilities(request):
#    pass
