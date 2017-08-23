from .models import (
    Activity, Entity, Agent, Used, WasGeneratedBy,
    WasAssociatedWith, WasAttributedTo, HadMember, WasDerivedFrom,
    WasInformedBy, HadStep, ActivityFlow, Collection
)
import logging


def find_entity(entity, prov, backcountdown, allbackward=False, members_flag=False, steps_flag=False, agent_flag=False):
    if backcountdown == 0:
        return prov

    # Look for entity in all possible relations,
    # follow these relations further recursively.
    # Follow at most backcountdown steps backward.

    if not allbackward:
        # well, it actually does not hurt to do it always,
        # it's just meaningless in the all-case
        backcountdown -= 1

    # First go through the 'short-cut' relation 'wasDerivedFrom'
    # because thus I only need to follow those nodes via the long
    # path, that were not visited before

    # wasDerivedFrom
    queryset = WasDerivedFrom.objects.filter(generatedEntity=entity.id)
    for wd in queryset:
        # add wasDerivedFrom-link
        if wd.id not in prov['wasDerivedFrom']:
            prov['wasDerivedFrom'][wd.id] = wd

        # add entity to prov, if not yet done
        if wd.usedEntity.id not in prov['entity']:
            prov['entity'][wd.usedEntity.id] = wd.usedEntity

            # continue with pre-decessor
            prov = find_entity(wd.usedEntity, prov, backcountdown,
                allbackward=allbackward,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)


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
            prov = find_activity(wg.activity, prov, backcountdown,
                allbackward=allbackward,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)

        #else:
        #    if not allbackward:
            # follow this activity in any case, even if it was found before,
            # because it may happen that this path is shorter than the one
            # before, and thus more relations need to be followed;
            # except, if all prov. info is required anyway
        #        prov = find_activity(wg.activity, prov, backcountdown, allbackward)



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
            prov = find_entity(h.collection, prov, backcountdown,
                allbackward=allbackward,
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
                prov = find_entity(h.entity, prov, backcountdown,
                    allbackward=allbackward,
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
            prov = find_agent(wa.agent, prov, backcountdown,
                allbackward=allbackward,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)


    # When I end up here, then I have reached an endpoint in the graph
    return prov


def find_activity(activity, prov, backcountdown, allbackward=False, members_flag=False, steps_flag=False, agent_flag=False):
    if backcountdown == 0:
        return prov

    # decrease countdown, unless ALL is desired (-1)
    if not allbackward:
        backcountdown -= 1

    # First check the 'shortcut' relationship 'wasInformedBy',
    # so I get the potentially farthest path first and do not
    # need to follow paths of already visited edges.

    # wasInformedBy
    queryset = WasInformedBy.objects.filter(informed=activity.id)
    for wi in queryset:

        # add relationship to prov
        if wi.id not in prov['wasInformedBy']:
            prov['wasInformedBy'][wi.id] = wi

        # add activity(flow) to prov
        activity_type = get_activity_type(wi.informant.id)
        if wi.informant.id not in prov[activity_type]:
            prov[activity_type][wi.informant.id] = wi.informant

            # follow provenance along this activity(flow)
            prov = find_activity(wi.informant, prov, backcountdown,
                allbackward=allbackward,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)

    # we won't check reverse direction, i.e. do not check, if this activity
    # has informed other activities (no future tracking)

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
            prov = find_entity(u.entity, prov, backcountdown,
                allbackward=allbackward,
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
            prov = find_agent(wa.agent, prov, backcountdown,
                allbackward=allbackward,
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
            prov = find_activity(h.activityFlow, prov, backcountdown,
                allbackward=allbackward,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)


    # hadStep, from activityflow to activity direction
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
                prov = find_activity(h.activity, prov, backcountdown,
                    allbackward=allbackward,
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


def find_agent(agent, prov, backcountdown, allbackward=False, members_flag=False, steps_flag=False, agent_flag=False):
    if backcountdown == 0:
        return prov

    # decrease countdown, unless ALL is desired (-1)
    if not allbackward:
        backcountdown -= 1

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
            prov = find_activity(wa.activity, prov, backcountdown,
                allbackward=allbackward,
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
            prov = find_entity(wa.entity, prov, backcountdown,
                allbackward=allbackward,
                members_flag=members_flag,
                steps_flag=steps_flag,
                agent_flag=agent_flag)

    return prov
