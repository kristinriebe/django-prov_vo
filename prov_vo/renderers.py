from __future__ import unicode_literals

import json

from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.six.moves import StringIO
from django.utils.encoding import smart_text
from django.utils.encoding import smart_unicode
from django.utils import timezone
from rest_framework.renderers import BaseRenderer
from lxml import etree

class PROVJSONRenderer(BaseRenderer):
    def render(self, data):
        # remove empty dicts
        for key, value in data.iteritems():
            if len(value) == 0:
                data.pop(key)

        string = json.dumps(data,
                #sort_keys=True,
                indent=4
            )

        return string


class PROVXMLRenderer(BaseRenderer):
    def render(self, data):
        # remove empty dicts
        for key, value in data.iteritems():
            if len(value) == 0:
                data.pop(key)

        nsmap = {}
        for prefix, ns in data['prefix'].iteritems():
            nsmap[prefix] = ns
        data.pop('prefix')
        PROV = "{%s}" % nsmap['voprov']
        root = etree.Element(PROV+'document', nsmap=nsmap)

        reference_list = ['voprov:description', 'voprov:activity', 'voprov:entity',
                'voprov:agent', 'voprov:influencer', 'voprov:influencee',
                'voprov:informed', 'voprov:informant', 'voprov:usedEntity',
                'voprov:generatedEntity', 'voprov:collection', 'voprov:activityFlow',
                'voprov:activityDescription', 'voprov:entityDescription']

        # Sort attributes: 1. mandatory att., 2. optional att. in alphabetical order
        # => Done by sorting fields in serializers
        for classkey in data:
            for e in data[classkey]:
                leaf = etree.SubElement(root, PROV+classkey)

                for attribute in data[classkey][e]:
                    if attribute == 'voprov:id':
                        leaf.attrib[PROV+'id'] = data[classkey][e]['voprov:id']
                    else:
                        att_ns = attribute.split(':')[0]
                        NS = "{%s}" % nsmap[att_ns]
                        att_name = attribute.split(':')[1]
                        leaf2 = etree.SubElement(leaf, NS+att_name)
                        if attribute in reference_list:
                            leaf2.attrib[PROV+'ref'] = data[classkey][e][attribute]
                        else:
                            leaf2.text = data[classkey][e][attribute]

        xml = etree.tostring(root, pretty_print=True)

        return xml


class W3CPROVXMLRenderer(BaseRenderer):
    def render(self, data):

        # remove empty dicts
        for key, value in data.iteritems():
            if len(value) == 0:
                data.pop(key)

        nsmap = {}
        for prefix, ns in data['prefix'].iteritems():
            nsmap[prefix] = ns
        data.pop('prefix')
        PROV = "{%s}" % nsmap['prov']
        root = etree.Element(PROV+'document', nsmap=nsmap)

        reference_list = ['prov:activity', 'prov:entity',
                'prov:agent', 'prov:influencer', 'prov:influencee',
                'prov:informed', 'prov:informant', 'prov:usedEntity',
                'prov:generatedEntity', 'prov:collection',
                'voprov:activityFlow',
                'voprov:activityDescription', 'voprov:entityDescription']

        # Sort attributes: 1. mandatory att., 2. optional att. in alphabetical order
        # => Done by sorting fields in serializers
        for classkey in data:
            for e in data[classkey]:
                leaf = etree.SubElement(root, PROV+classkey)
                for attribute in data[classkey][e]:
                    if attribute == 'prov:id':
                        leaf.attrib[PROV+'id'] = data[classkey][e][attribute]
                    else:
                        att_ns = attribute.split(':')[0]
                        NS = "{%s}" % nsmap[att_ns]
                        att_name = attribute.split(':')[1]
                        leaf2 = etree.SubElement(leaf, NS+att_name)

                        if attribute in reference_list:
                            leaf2.attrib[PROV+'ref'] = data[classkey][e][attribute]
                        elif attribute == 'voprov:description':
                            # embed the descriptions here
                            for desc_attribute in data[classkey][e][attribute]:
                                if desc_attribute == 'prov:id':  # or if voprov:id
                                    leaf2.attrib[PROV+'id'] = data[classkey][e][attribute][desc_attribute]
                                else:
                                    att_ns = desc_attribute.split(':')[0]
                                    NS = "{%s}" % nsmap[att_ns]
                                    att_name = desc_attribute.split(':')[1]
                                    leaf3 = etree.SubElement(leaf2, NS+att_name)
                                    leaf3.text = data[classkey][e][attribute][desc_attribute]
                        else:
                            leaf2.text = data[classkey][e][attribute]

        xml = etree.tostring(root, pretty_print=True)

        return xml


class PROVNBaseRenderer(BaseRenderer):

    def get_value(self, obj, key):
        marker = "-"

        # check, if the key exists with prov or voprov namespace;
        # if yes: return value, if not: return marker
        # only needed for positional arguments
        prov_key = "prov:%s" % key
        voprov_key = "voprov:%s" % key

        if prov_key in obj:
            return str(obj.pop(prov_key))
        elif voprov_key in obj:
            return str(obj.pop(voprov_key))
        else:
            return marker

    def add_relation_id(self, string, obj):

        value = None
        if "prov:id" in obj:
            value = str(obj.pop("prov:id"))
            if ":" not in value:
                # Then this id is just an internal id here,
                # skip it in PROV-N serialization.
                # (Adding a blank as identifier namespace will not validate in ProvStore, thus don't use it)
                # value = "%s:%s" % (namespace, value)
                value = None

        if value is not None:
            string += "%s; " % value
        # else: return original string

        return string

    def add_optional_attributes(self, string, obj):
        # construct string for optional attributes,
        # and add to provn-string (just before final closing ")" )
        attributes = ""
        for key, val in obj.iteritems():
            attributes += '%s="%s", ' % (key, val)

        # add to string (and remove final comma)
        if attributes:
            string = string.replace(")", ", [%s])" % attributes.rstrip(', '))

        return string


class ActivityPROVNRenderer(PROVNBaseRenderer):

    def render(self, activity):
        string = "activity("\
            + self.get_value(activity, "id") + ", "\
            + self.get_value(activity, "startTime") + ", "\
            + self.get_value(activity, "endTime")\
            + ")"

        string = self.add_optional_attributes(string, activity)

        return string


class ActivityFlowPROVNRenderer(PROVNBaseRenderer):

    def render(self, activityFlow):
        string = "activityFlow("\
            + self.get_value(activityFlow, "id") + ", "\
            + self.get_value(activityFlow, "startTime") + ", "\
            + self.get_value(activityFlow, "endTime")\
            + ")"

        string = self.add_optional_attributes(string, activityFlow)

        return string


class EntityPROVNRenderer(PROVNBaseRenderer):

    def render(self, entity):
        string = "entity(" + self.get_value(entity, "id") + ")"
        string = self.add_optional_attributes(string, entity)

        return string


class AgentPROVNRenderer(PROVNBaseRenderer):

    def render(self, agent):
        string = "agent(" + self.get_value(agent, "id") + ")"
        string = self.add_optional_attributes(string, agent)

        return string


class ParameterPROVNRenderer(PROVNBaseRenderer):

    def render(self, parameter):
        string = "parameter("
        string += self.get_value(parameter, "id") + ", "
        string += self.get_value(parameter, "activity") + ", "
        string += self.get_value(parameter, "value")
        string += ")"


        # add all other optional attributes in []
        string = self.add_optional_attributes(string, parameter)

        return string


class ParameterDescriptionPROVNRenderer(PROVNBaseRenderer):

    def render(self, parameterDescription):
        string = "parameterDescription("
        string += self.get_value(parameterDescription, "id") + ", "
        string += self.get_value(parameterDescription, "name")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, parameterDescription)

        return string


class ActivityDescriptionPROVNRenderer(PROVNBaseRenderer):

    def render(self, activityDescription):
        string = "activityDescription("
        string += self.get_value(activityDescription, "id")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, activityDescription)

        return string


class EntityDescriptionPROVNRenderer(PROVNBaseRenderer):

    def render(self, entityDescription):
        string = "entityDescription("
        string += self.get_value(entityDescription, "id")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, entityDescription)

        return string


class UsedPROVNRenderer(PROVNBaseRenderer):

    def render(self, used):
        string = "used("

        # id is optional, but we have an id in the database, thus include it
        string = self.add_relation_id(string, used)

        # activity is mandatory:
        string += self.get_value(used, "activity") + ", "

        # entity is optional in W3C, but it's a positional argument
        string += self.get_value(used, "entity") + ", "

        # time is optional in W3C, but it's a positional argument
        string += self.get_value(used, "time") + ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, used)

        return string


class UsedDescriptionPROVNRenderer(PROVNBaseRenderer):

    def render(self, usedDescription):
        string = "usedDescription("

        # add id + references
        string += self.get_value(usedDescription, "id") + ", "
        string += self.get_value(usedDescription, "activityDescription") + ", "
        string += self.get_value(usedDescription, "entityDescription") + ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, usedDescription)

        return string


class WasGeneratedByPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasGeneratedBy):
        string = "wasGeneratedBy("

        # id is optional
        string = self.add_relation_id(string, wasGeneratedBy)

        # entity is mandatory:
        string += self.get_value(wasGeneratedBy, "entity") + ", "

        # activity is optional in W3C, but it's a positional argument
        string += self.get_value(wasGeneratedBy, "activity") + ", "

        # time is optional in W3C, but it's a positional argument
        string += self.get_value(wasGeneratedBy, "time")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasGeneratedBy)

        return string


class WasGeneratedByDescriptionPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasGeneratedByDescription):
        string = "wasGeneratedByDescription("

        # add id + references
        string += self.get_value(wasGeneratedByDescription, "id") + ", "
        string += self.get_value(wasGeneratedByDescription, "entityDescription") + ", "
        string += self.get_value(wasGeneratedByDescription, "activityDescription") + ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasGeneratedByDescription)

        return string


class WasAssociatedWithPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasAssociatedWith):
        string = "wasAssociatedWith("

        # id is optional
        string = self.add_relation_id(string, wasAssociatedWith)
        string += self.get_value(wasAssociatedWith, "activity") + ", "
        string += self.get_value(wasAssociatedWith, "agent") + ", "
        string += self.get_value(wasAssociatedWith, "plan")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasAssociatedWith)

        return string


class WasAttributedToPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasAttributedTo):
        string = "wasAttributedTo("

        # id is optional, but I have an id in the database, thus include it
        string = self.add_relation_id(string, wasAttributedTo)
        string += self.get_value(wasAttributedTo, "entity") + ", "
        string += self.get_value(wasAttributedTo, "agent")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasAttributedTo)

        return string


class HadMemberPROVNRenderer(PROVNBaseRenderer):

    def render(self, hadMember):
        string = "hadMember("

        # does not have an id nor optional attributes in W3C
        string += self.get_value(hadMember, "collection") + ", "
        string += self.get_value(hadMember, "entity")

        string += ")"

        return string


class WasDerivedFromPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasDerivedFrom):
        string = "wasDerivedFrom("

        string = self.add_relation_id(string, wasDerivedFrom)
        string += self.get_value(wasDerivedFrom, "generatedEntity") + ", "
        string += self.get_value(wasDerivedFrom, "usedEntity") + ", "
        string += self.get_value(wasDerivedFrom, "activity") + ", "
        string += self.get_value(wasDerivedFrom, "generation") + ", "
        string += self.get_value(wasDerivedFrom, "usage")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasDerivedFrom)

        return string


class HadStepPROVNRenderer(PROVNBaseRenderer):

    def render(self, hadStep):
        string = "hadStep("

        string = self.add_relation_id(string, hadStep)
        string += self.get_value(hadStep, "activityFlow") + ", "
        string += self.get_value(hadStep, "activity")

        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, hadStep)

        return string


class WasInformedByPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasInformedBy):
        string = "wasInformedBy("

        string = self.add_relation_id(string, wasInformedBy)
        string += self.get_value(wasInformedBy, "informed") + ", "
        string += self.get_value(wasInformedBy, "informant")
        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasInformedBy)

        return string


class WasInfluencedByPROVNRenderer(PROVNBaseRenderer):

    def render(self, wasInfluencedBy):
        string = "wasInfluencedBy("

        string = self.add_relation_id(string, wasInfluencedBy)
        string += self.get_value(wasInfluencedBy, "influencee") + ", "
        string += self.get_value(wasInfluencedBy, "influencer")

        string += ")"

        # add all other optional attributes in []
        string = self.add_optional_attributes(string, wasInfluencedBy)

        return string


class PROVNRenderer(PROVNBaseRenderer):
    """
    Takes a list of ordered Python dictionaries (serialized data)
    and returns a PROV-N string
    """

    def render(self, data):

        string = "document\n"
        for p_id, p in data['prefix'].iteritems():
            string += "prefix %s <%s>\n" % (p_id, p)
        string += "\n"

        for a_id, a in data['activity'].iteritems():
            string += ActivityPROVNRenderer().render(a) + "\n"

        if 'activityFlow' in data:
            for a_id, a in data['activityFlow'].iteritems():
                string += ActivityFlowPROVNRenderer().render(a) + "\n"

        if 'activityDescription' in data:
            for a_id, a in data['activityDescription'].iteritems():
                string += ActivityDescriptionPROVNRenderer().render(a) + "\n"

        if 'parameter' in data:
            for p_id, p in data['parameter'].iteritems():
                string += ParameterPROVNRenderer().render(p) + "\n"

        if 'parameterDescription' in data:
            for h_id, h in data['parameterDescription'].iteritems():
                string += ParameterDescriptionPROVNRenderer().render(h) + "\n"

        for e_id, e in data['entity'].iteritems():
            string += EntityPROVNRenderer().render(e) + "\n"

        if 'entityDescription' in data:
            for a_id, a in data['entityDescription'].iteritems():
                string += EntityDescriptionPROVNRenderer().render(a) + "\n"

        for a_id, a in data['agent'].iteritems():
            string += AgentPROVNRenderer().render(a) + "\n"

        for u_id, u in data['used'].iteritems():
            string += UsedPROVNRenderer().render(u) + "\n"

        if 'usedDescription' in data:
            for u_id, u in data['usedDescription'].iteritems():
                string += UsedDescriptionPROVNRenderer().render(u) + "\n"

        for w_id, w in data['wasGeneratedBy'].iteritems():
            string += WasGeneratedByPROVNRenderer().render(w) + "\n"

        if 'wasGeneratedByDescription' in data:
            for w_id, w in data['wasGeneratedByDescription'].iteritems():
                string += WasGeneratedByDescriptionPROVNRenderer().render(w) + "\n"

        for w_id, w in data['wasAssociatedWith'].iteritems():
            string += WasAssociatedWithPROVNRenderer().render(w) + "\n"

        for w_id, w in data['wasAttributedTo'].iteritems():
            string += WasAttributedToPROVNRenderer().render(w) + "\n"

        for h_id, h in data['hadMember'].iteritems():
            string += HadMemberPROVNRenderer().render(h) + "\n"

        for w_id, w in data['wasDerivedFrom'].iteritems():
            string += WasDerivedFromPROVNRenderer().render(w) + "\n"

        if 'hadStep' in data:
            for h_id, h in data['hadStep'].iteritems():
                string += HadStepPROVNRenderer().render(h) + "\n"

        if 'wasInformedBy' in data:
            for w_id, w in data['wasInformedBy'].iteritems():
                string += WasInformedByPROVNRenderer().render(w) + "\n"

        if 'wasInfluencedBy' in data:
            for w_id, w in data['wasInfluencedBy'].iteritems():
                string += WasInfluencedByPROVNRenderer().render(w) + "\n"

        string += "endDocument"

        return string
