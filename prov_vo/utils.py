from .models import (
    Activity, Entity, Agent, Used, WasGeneratedBy,
    WasAssociatedWith, WasAttributedTo, HadMember, WasDerivedFrom,
    WasInformedBy, HadStep, ActivityFlow, Collection
)


# Helper functions for tracking provenance paths
def find_entity_graph(entity, prov, collection="include"):

    # always check membership to collection first (and follow its provenance),
    # no matter if it's a collection or not
    queryset = HadMember.objects.filter(entity=entity.id)
    for h in queryset:
        print "Entity "+ entity.id + " is member of collection: ", h.collection.id

        # add entity to prov-json, if not yet done
        if h.collection.id not in prov['map_nodes_ids']:
            prov['nodes_dict'].append({'name': h.collection.name, 'type': 'entity'})
            prov['map_nodes_ids'][h.collection.id] = prov['count_nodes']
            prov['count_nodes'] = prov['count_nodes'] + 1

            # follow this collection's provenance (if it was not recorded before)
            prov = find_entity_graph(h.collection, prov, collection=collection)
        else:
            # just find its id:
            id1 = prov['map_nodes_ids'] # not needed, is found below anyway

        # add hadMember-link:
        # but only, if not yet recorded -> how to check?
        prov['links_dict'].append({"source": prov['map_nodes_ids'][h.collection.id], "target": prov['map_nodes_ids'][h.entity.id], "value": 0.2, "type": "hadMember"})
        prov['count_link'] = prov['count_link'] + 1


    # track the provenance information backwards, but possibly only/not for collections!
    if collection == "exclude":
        # return immediately, if it is a collection
        if entity.type == "prov:collection":
            return prov
    elif collection == "only":
        # only continue, if it is a collection, i.e. return if it is not
        if entity.type != "prov:collection":
            return prov
    else:
        # continue, independent of collection type or not
        pass

    queryset = WasGeneratedBy.objects.filter(entity=entity.id)
    for wg in queryset:
        print "Entity " + entity.id + " wasGeneratedBy activity: ", wg.activity.id

        # add activity to prov-json for graphics, if not yet done
        # (use map_activity_ids for easier checking)

        if wg.activity.id not in prov['map_nodes_ids']:
            prov['nodes_dict'].append({'name': wg.activity.name, 'type': 'activity'})
            prov['map_nodes_ids'][wg.activity.id] = prov['count_nodes']
            prov['count_nodes'] = prov['count_nodes'] + 1

            # follow provenance along this activity
            prov = find_activity_graph(wg.activity, prov, collection=collection)

        # add wasGeneratedBy-link
        prov['links_dict'].append({"source": prov['map_nodes_ids'][wg.entity.id], "target": prov['map_nodes_ids'][wg.activity.id], "value": 0.2, "type": "wasGeneratedBy"})
        prov['count_link'] = prov['count_link'] + 1


    queryset = WasDerivedFrom.objects.filter(generatedEntity=entity.id)
    # this relation is unique, there can be only one ... or not?
    for wd in queryset:
        print "Entity " + entity.id + " wasDerivedFrom entity ", wd.usedEntity.id

        # add entity to prov-json, if not yet done
        if wd.usedEntity.id not in prov['map_nodes_ids']:
            prov['nodes_dict'].append({'name': wd.usedEntity.name, 'type': 'entity'})
            prov['map_nodes_ids'][wd.usedEntity.id] = prov['count_nodes']
            prov['count_nodes'] = prov['count_nodes'] + 1

            # continue with pre-decessor
            prov = find_entity_graph(wd.usedEntity, prov, collection=collection)

        # add hadMember-link (in any case)
        prov['links_dict'].append({"source": prov['map_nodes_ids'][entity.id], "target": prov['map_nodes_ids'][wd.usedEntity.id], "value": 0.2, "type": "wasDerivedFrom"})
        prov['count_link'] = prov['count_link'] + 1


    # if nothing found until now, then I have reached an endpoint in the graph
    #print "Giving up, no more provenance for entity found."
    return prov


def find_activity_graph(activity, prov, collection="include"):
# basic = only collections; detail = no collections

    # Check used relations
    queryset = Used.objects.filter(activity=activity.id)
    for u in queryset:

        print "Activity " + activity.id + " used entity ", u.entity.id

        # only continue, if collection or no collection or always
        cont = True
        if collection == "exclude":
            # skip, if it is a collection
            if u.entity.type == "prov:collection":
                cont = False
        elif collection == "only":
            # only continue, if it is a collection, i.e. skip if it is not
            if u.entity.type != "prov:collection":
                cont = False
        else:
            # continue, independent of collection type or not
            pass

        if cont:
            # add entity to prov-json, if not yet done
            if (u.entity.id not in prov['map_nodes_ids']):
                prov['nodes_dict'].append({'name': u.entity.name, 'type': 'entity'})
                prov['map_nodes_ids'][u.entity.id] = prov['count_nodes']
                prov['count_nodes'] = prov['count_nodes'] + 1

                # follow this entity's provenance
                prov = find_entity_graph(u.entity, prov, collection=collection)

            # add used-link:
            prov['links_dict'].append({"source": prov['map_nodes_ids'][activity.id], "target": prov['map_nodes_ids'][u.entity.id], "value": 0.2, "type": "used"})
            prov['count_link'] = prov['count_link'] + 1

    #print "Giving up, no more provenance for activity found."
    return prov



def find_entity(entity, prov, backcountdown, follow=True):
    # Look for entity in all possible relations,
    # follow these relations further recursively.
    # If follow is False, then do not follow the relations any futher,
    # except for wasGeneratedBy-activity: here one more step is done
    # in order to find and record the used entities.

    # track the provenance information backwards via WasGeneratedBy
    queryset = WasGeneratedBy.objects.filter(entity=entity.id)
    for wg in queryset:
        print "Entity "+ entity.id + " wasGeneratedBy activity: ", wg.activity.id

        # add activity(flow) to prov-list, IF not existing there already
        activity_type = get_activity_type(wg.activity.id)
        if wg.activity.id not in prov[activity_type]:
            prov[activity_type][wg.activity.id] = wg.activity

            # follow provenance along this activity(flow)
            if follow:
                prov = find_activity(wg.activity, prov, backcountdown, follow=True)
            #else:
            # follow only for one step
            #    prov = find_activity(wg.activity, prov, follow=False)

        # add wasGeneratedBy-link
        prov['wasGeneratedBy'][wg.id] = wg


    # track backwards via wasDerivedFrom
    queryset = WasDerivedFrom.objects.filter(generatedEntity=entity.id)
    for wd in queryset:
        print "Entity " + entity.id + " wasDerivedFrom entity ", wd.usedEntity.id

        # add entity to prov, if not yet done
        if wd.usedEntity.id not in prov['entity']:
            prov['entity'][wd.usedEntity.id] = wd.usedEntity

            # continue with pre-decessor
            if follow:
                prov = find_entity(wd.usedEntity, prov, backcountdown, follow=True)

        # add wasDerivedFrom-link (in any case)
        prov['wasDerivedFrom'][wd.id] = wd


    # check membership to collection
    queryset = HadMember.objects.filter(entity=entity.id)
    # TODO: the entity could also be the collection!! I.e. need to check also: collection=entity.id
    # actually, entities cannot belong to more than one collection,
    # but we'll allow it here for now ...
    for h in queryset:
        print "Entity "+ entity.id + " is member of collection: ", h.collection.id, follow

        # add entity to prov-json, if not yet done
        if h.collection.id not in prov['entity']:
            prov['entity'][h.collection.id] = h.collection

            # follow this collection's provenance (if it was not recorded before)
            if follow:
                prov = find_entity(h.collection, prov, backcountdown, follow=True)
            else:
                # only if there was no wasDerivedFrom and wasGeneratedBy so far,
                # only then follow the collection's provenance one more step
                if len(prov['wasGeneratedBy']) == 0 and len(prov['wasDerivedFrom']) == 0:
                    prov = find_entity(h.collection, prov, follow=False)
                pass

        # add hadMember-link:
        prov['hadMember'][h.id] = h


    # check agent relation (attribution)
    queryset = WasAttributedTo.objects.filter(entity=entity.id)
    for wa in queryset:
        print "Entity " + entity.id + " WasAttributedTo agent ", wa.agent.id

        if wa.agent.id not in prov['agent']:
            # add agent to prov
            prov['agent'][wa.agent.id] = wa.agent

        # add wasAttributedto relationship
        prov['wasAttributedTo'][wa.id] = wa

    # if nothing found until now, then I have reached an endpoint in the graph
    return prov


def find_activity(activity, prov, backcountdown, follow=True):

    queryset = Used.objects.filter(activity=activity.id)

    # used relations
    for u in queryset:
        # because only want details, no collection, return if it is a collection
        #if "prov:collection" in u.entity.type.split(';'):
        #    return prov
        print "Activity " + activity.id + " used entity ", u.entity.id

        # add entity to prov, if not yet done
        if u.entity.id not in prov['entity']:
            prov['entity'][u.entity.id] = u.entity

            # follow this entity's provenance
            if follow:
                prov = find_entity(u.entity, prov, backcountdown, follow=True)

        # add used-link:
        prov['used'][u.id] = u
    #print "Giving up, no more provenance for activity %s found." % activity.id

    # check agent relation (association)
    queryset = WasAssociatedWith.objects.filter(activity=activity.id)
    for wa in queryset:
        print "Agent " + wa.agent.id + " WasAssociatedWith activity ", wa.activity.id

        if wa.agent.id not in prov['agent']:
            # add agent to prov
            prov['agent'][wa.agent.id] = wa.agent

        # add relationship to prov
        prov['wasAssociatedWith'][wa.id] = wa

    # wasInformedBy
    queryset = WasInformedBy.objects.filter(informed=activity.id)
    for wi in queryset:
        print "Activity " + wi.informed.id + " WasInformedBy activity ", wi.informant.id

        # check, if it is an activityFlow or not, add to prov
        # add activity(flow) to prov
        activity_type = get_activity_type(wi.informant.id)
        if wi.informant.id not in prov[activity_type]:
            prov[activity_type][wi.informant.id] = wi.informant

            # follow provenance along this activity(flow)
            if follow:
                prov = find_activity(wi.informant, prov, backcountdown, follow=True)

        # add relationship to prov
        prov['wasInformedBy'][wi.id] = wi
    # we won't check backwards direction, i.e. do not check, if this activity
    # has informed other activities (no future tracking)

    # hadStep
    queryset = HadStep.objects.filter(activity=activity.id)
    for h in queryset:
        print "ActivityFlow " + h.activityFlow.id + " hadStep activity ", activity.id

        # add activityFlow, if not yet done
        if h.activityFlow.id not in prov['activityFlow']:
            prov['activityFlow'][h.activityFlow.id] = h.activityFlow

            # follow provenance along this activity(flow)
            if follow:
                prov = find_activity(h.activityFlow, prov, backcountdown, follow=True)

        # add relationship to prov
        prov['hadStep'][h.id] = h

    # hadStep, other direction
    # -> do not follow this, may be too much!
    # queryset = HadStep.objects.filter(activityFlow=activity.id)
    # for h in queryset:
    #     print "ActivityFlow " + h.activityFlow.id + " hadStep activity ", h.activity.id

    #     # add activity, if not yet done
    #     activity_type = get_activity_type(h.activity.id)
    #     if h.activity.id not in prov[activity_type]:
    #         prov[activity_type][h.activity.id] = h.activity

    #         # follow provenance along this activity(flow)
    #         #if follow:
    #         #    prov = find_activity(h.activity, prov, follow=True)

    #     # add relationship to prov
    #     prov['hadStep'][h.id] = h



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
