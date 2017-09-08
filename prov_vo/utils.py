from .models import (
    Activity, Entity, Agent, Used, WasGeneratedBy,
    WasAssociatedWith, WasAttributedTo, HadMember, WasDerivedFrom,
    WasInformedBy, HadStep, ActivityFlow, Collection
)
import logging
from django.http import QueryDict

class InvalidData(Exception):
    pass


class QueryDictDALI(QueryDict):
    """
    Same as QueryDict class, but can turn URL parameter names to
    upper case so they can be treated as case-insensitive as
    required by VO's DALI spec.
    Also provides the function getsingle for getting the single value
    of a parameter that shall occur only once (at most), and raises
    a ValueError if this is violated.

    Example:
    QueryDictDALI.getlist('ID') will return values parameter ID, id, Id and iD.
    Actually, need to enforce single value if expecting single value
    And that required parameters exist.
    """

    def __init__(self, querydict=None, uppercase=True):
        super(QueryDictDALI, self).__init__()
        self._mutable = True
        if querydict:

            # copy values
            for key, values in querydict.iterlists():
                self.setlist(key, values)

            # make it all upper case
            if uppercase:
                self.make_upper_case_parameter_names()

    def getsingle(self, key, default=None):
        """
        Return the data value for the passed key. If key doesn't exist
        or value is an empty list, return `default`.
        Ensure that the key occured at most one single time, otherwise raise error
        """
        try:
            val = self.getlist(key)
        except KeyError:
            return default
        if val == []:
            return default
        if len(list(val)) > 1:
           raise InvalidData('Bad request: parameter %s must occur only once or not at all.' % key)
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



def track_entity(entity, prov, countdown, all_flag=False, direction='BACK', members_flag=False, steps_flag=False, agent_flag=False):
    if countdown == 0:
        return prov

    # Look for entity in all possible relations,
    # follow these relations further recursively.

    # Follow at most countdown steps backward
    # (might even be set in all_flag=True case).
    countdown -= 1

    # First go through the 'short-cut' relation 'wasDerivedFrom'
    # because thus I only need to follow those nodes via the long
    # path, that were not visited before

    # wasDerivedFrom
    if direction == 'BACK':
        queryset = WasDerivedFrom.objects.filter(generatedEntity=entity.id)
    else:
        queryset = WasDerivedFrom.objects.filter(usedEntity=entity.id)

    for wd in queryset:
        if direction == 'BACK':
            nextnode = wd.usedEntity
        else:
            nextnode = wd.generatedEntity

        # add wasDerivedFrom-link
        if wd.id not in prov['wasDerivedFrom']:
            prov['wasDerivedFrom'][wd.id] = wd

        # add entity to prov, if not yet done
        if nextnode.id not in prov['entity']:
            prov['entity'][nextnode.id] = nextnode

            # continue with pre-decessor
            prov = track_entity(nextnode, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)


    if direction == 'BACK':

        # wasGeneratedBy
        queryset = WasGeneratedBy.objects.filter(entity=entity.id)
        for wg in queryset:
            # add wasGeneratedBy-link
            # --> need to check if it's already there, because I may have
            # to walk nodes and relations twice for counting properly
            # (if there is a shortcut somewhere)
            if wg.id not in prov['wasGeneratedBy']:
                prov['wasGeneratedBy'][wg.id] = wg

            # add activity(flow) to prov-list, if not included already
            activity_type = get_activity_type(wg.activity.id)
            if wg.activity.id not in prov[activity_type]:
                prov[activity_type][wg.activity.id] = wg.activity

                # follow activity further (but only, if not visited before)
                prov = track_activity(wg.activity, prov, countdown,
                    all_flag=all_flag,
                    direction=direction,
                    members_flag=members_flag,
                    steps_flag=steps_flag,
                    agent_flag=agent_flag)

            #else:
            #    if not all_flag:
                # follow this activity in any case, even if it was found before,
                # because it may happen that this path is shorter than the one
                # before, and thus more relations need to be followed;
                # except, if all prov. info is required anyway
            #        prov = track_activity(wg.activity, prov, countdown, all_flag)

    else:
        # in FORTH case, we have to find out where entities are being used:

        # used relations
        queryset = Used.objects.filter(entity=entity.id)
        for u in queryset:
            # add used-link, if not yet done
            if u.id not in prov['used']:
                prov['used'][u.id] = u

            # add activity to prov, if not yet done
            activity_type = get_activity_type(wg.activity.id)
            if u.activity.id not in prov[activity_type]:
                prov[activity_type][u.activity.id] = u.activity

                # follow this activity's provenance (always)
                prov = track_activity(u.activity, prov, countdown,
                    all_flag=all_flag,
                    direction=direction,
                    members_flag=members_flag,
                    steps_flag=steps_flag,
                    agent_flag=agent_flag)



    # check membership to collection
    queryset = HadMember.objects.filter(entity=entity.id)
    for h in queryset:
    #     print "Entity "+ entity.id + " is member of collection: ", h.collection.id, follow

        # add relation to prov
        if h.id not in prov['hadMember']:
            prov['hadMember'][h.id] = h

        # add entity to prov-json, if not yet done
        if h.collection.id not in prov['entity']:
            prov['entity'][h.collection.id] = h.collection

            # follow further
            prov = track_entity(h.collection, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)



    # hadMember (check for members)
    if members_flag:
        queryset = HadMember.objects.filter(collection=entity.id)
        for h in queryset:
            # add relation to prov
            if h.id not in prov['hadMember']:
                prov['hadMember'][h.id] = h

            # add entity to prov
            if h.entity.id not in prov['entity']:
                prov['entity'][h.entity.id] = h.entity

                # follow further
                prov = track_entity(h.entity, prov, countdown,
                    all_flag=all_flag,
                    direction=direction,
                    members_flag=members_flag,
                    steps_flag=steps_flag,
                    agent_flag=agent_flag)




    # check agent relation (attribution)
    queryset = WasAttributedTo.objects.filter(entity=entity.id)
    for wa in queryset:
        # add wasAttributedto relationship
        if wa.id not in prov['wasAttributedTo']:
            prov['wasAttributedTo'][wa.id] = wa

        # add agent to prov
        if wa.agent.id not in prov['agent']:
            prov['agent'][wa.agent.id] = wa.agent

        # do not follow agent further, unless flag is set
        if agent_flag:
            prov = track_agent(wa.agent, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)


    # When I end up here, then I have reached an endpoint in the graph
    return prov


def track_activity(activity, prov, countdown, all_flag=False, direction='BACK', members_flag=False, steps_flag=False, agent_flag=False):
    if countdown == 0:
        return prov

    # decrease countdown
    countdown -= 1

    # First check the 'shortcut' relationship 'wasInformedBy',
    # so I get the potentially farthest path first and do not
    # need to follow paths of already visited edges.

    # wasInformedBy
    if direction == 'BACK':
        queryset = WasInformedBy.objects.filter(informed=activity.id)
    else:
        queryset = WasInformedBy.objects.filter(informant=activity.id)

    for wi in queryset:

        if direction == 'BACK':
            nextnode = wi.informant
        else:
            nextnode = wi.informed

        # add relationship to prov
        if wi.id not in prov['wasInformedBy']:
            prov['wasInformedBy'][wi.id] = wi

        # add activity(flow) to prov
        activity_type = get_activity_type(nextnode.id)
        if nextnode.id not in prov[activity_type]:
            prov[activity_type][nextnode.id] = nextnode

            # follow provenance along this activity(flow)
            prov = track_activity(nextnode, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)

    if direction == 'BACK':
        # used relations
        queryset = Used.objects.filter(activity=activity.id)
        for u in queryset:
            # add used-link, if not yet done
            if u.id not in prov['used']:
                prov['used'][u.id] = u

            # add entity to prov, if not yet done
            if u.entity.id not in prov['entity']:
                prov['entity'][u.entity.id] = u.entity

                # follow this entity's provenance (always)
                prov = track_entity(u.entity, prov, countdown,
                    all_flag=all_flag,
                    direction=direction,
                    members_flag=members_flag,
                    steps_flag=steps_flag,
                    agent_flag=agent_flag)

    else:
        # reverse, i.e. forward direction, thus need to find
        # produced entities for this activity

        # wasGeneratedBy
        queryset = WasGeneratedBy.objects.filter(activity=activity.id)
        for wg in queryset:
            # add wasGeneratedBy-link
            if wg.id not in prov['wasGeneratedBy']:
                prov['wasGeneratedBy'][wg.id] = wg

            # add entity to prov-list, if not included already
            if wg.entity.id not in prov['entity']:
                prov['entity'][wg.entity.id] = wg.entity

                # follow activity further (but only, if not visited before)
                prov = track_entity(wg.entity, prov, countdown,
                    all_flag=all_flag,
                    direction=direction,
                    members_flag=members_flag,
                    steps_flag=steps_flag,
                    agent_flag=agent_flag)



    # check agent relation (association)
    queryset = WasAssociatedWith.objects.filter(activity=activity.id)
    for wa in queryset:

        # add relationship to prov
        if wa.id not in prov['wasAssociatedWith']:
            prov['wasAssociatedWith'][wa.id] = wa

        # add agent to prov
        if wa.agent.id not in prov['agent']:
            prov['agent'][wa.agent.id] = wa.agent

        # do not follow agent further, unless flag is set
        if agent_flag:
            prov = track_agent(wa.agent, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)


    # hadStep - find activityFlows to which it belongs
    queryset = HadStep.objects.filter(activity=activity.id)
    for h in queryset:
        # add relationship to prov
        if h.id not in prov['hadStep']:
            prov['hadStep'][h.id] = h

        # add activityFlow, if not yet done
        if h.activityFlow.id not in prov['activityFlow']:
            prov['activityFlow'][h.activityFlow.id] = h.activityFlow

            # follow provenance along this activity(flow)
            prov = track_activity(h.activityFlow, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)


    # get member activities: follow hadStep from activityflow to activity
    if steps_flag:
        queryset = HadStep.objects.filter(activityFlow=activity.id)
        for h in queryset:
            # add relationship to prov
            if h.id not in prov['hadStep']:
                prov['hadStep'][h.id] = h

            # add activity, if not yet done
            activity_type = get_activity_type(h.activity.id)
            if h.activity.id not in prov[activity_type]:
                prov[activity_type][h.activity.id] = h.activity

                # follow provenance along this activity(flow)
                prov = track_activity(h.activity, prov, countdown,
                    all_flag=all_flag,
                    direction=direction,
                    members_flag=members_flag,
                    steps_flag=steps_flag,
                    agent_flag=agent_flag)

    return prov


def get_activity_type(activity_id):
    # check if it is an activityFlow or activity,
    # return string (what it is)
    afset = ActivityFlow.objects.filter(id=activity_id)
    if len(afset) > 0:
        activity_type = 'activityFlow'
    else:
        activity_type = 'activity'

    return activity_type


def track_agent(agent, prov, countdown, all_flag=False, direction='BACK', members_flag=False, steps_flag=False, agent_flag=False):
    if countdown == 0:
        return prov

    # decrease countdown
    countdown -= 1

    # Check possible agent relationships and follow corresponding activity/entity

    queryset = WasAssociatedWith.objects.filter(agent=agent.id)
    for wa in queryset:

        # add relationship to prov
        if wa.id not in prov['wasAssociatedWith']:
            prov['wasAssociatedWith'][wa.id] = wa

        # add activity, if not yet done
        activity_type = get_activity_type(wa.activity.id)
        if wa.activity.id not in prov[activity_type]:
            prov[activity_type][wa.activity.id] = wa.activity

            # follow provenance along this activity(flow)
            prov = track_activity(wa.activity, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)

    # check agent relation (attribution)
    queryset = WasAttributedTo.objects.filter(agent=agent.id)
    for wa in queryset:
        # add wasAttributedTo relationship
        if wa.id not in prov['wasAttributedTo']:
            prov['wasAttributedTo'][wa.id] = wa

        # add entity to prov-json, if not yet done
        if wa.entity.id not in prov['entity']:
            prov['entity'][wa.entity.id] = wa.entity

            # follow further
            prov = track_entity(wa.entity, prov, countdown,
                all_flag=all_flag,
                direction=direction,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)

    return prov
