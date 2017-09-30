from __future__ import unicode_literals

import json

from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.six.moves import StringIO
from django.utils.encoding import smart_text
from django.utils.encoding import smart_unicode
from django.utils import timezone
from rest_framework.renderers import BaseRenderer
import lxml.etree as etree  # for pretty printing xml


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

        for e_id, e in data['entity'].iteritems():
            string += EntityPROVNRenderer().render(e) + "\n"

        for a_id, a in data['agent'].iteritems():
            string += AgentPROVNRenderer().render(a) + "\n"

        for u_id, u in data['used'].iteritems():
            string += UsedPROVNRenderer().render(u) + "\n"

        for w_id, w in data['wasGeneratedBy'].iteritems():
            string += WasGeneratedByPROVNRenderer().render(w) + "\n"

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


class VosiAvailabilityRenderer(BaseRenderer):
        """
        Returns an xmlstream for VOSI availability/ endpoint
        """

        charset = 'utf-8'

        # namespace declarations
        ns_vosiavail = 'http://www.ivoa.net/xml/VOSIAvailability/v1.0'
        version = '1.1'

        comment = "<!--\n"\
                + " !  Generated using Django with SimplerXMLGenerator\n"\
                + " !  at "+str(timezone.now())+"\n"\
                + " !-->\n"


        def render(self, data, prettyprint=False):
            """
            parameters:
              data = dictionary of the things to be shown
              prettyprint = flag for pretty printing the xml output (including whitespace and linebreaks)
            """

            stream = StringIO()
            xml = SimplerXMLGenerator(stream, self.charset)

            xml.startDocument()

            # add a comment
            xml._write(self.comment)

            # add namespace definitions
            nsattrs = {}
            nsattrs['version'] = self.version
            #nsattrs['encoding'] = charser
            nsattrs['xmlns:vosi'] = self.ns_vosiavail
            #nsattrs['xmlns:xsi'] = self.ns_xsi
            #nsattrs['xmlns:vs'] = self.ns_vs

            # add root node
            xml.startElement('vosi:availability', nsattrs)

            # add mandatory node:
            xml.startElement('vosi:available', {})
            xml.characters(smart_unicode(data['available']))
            xml.endElement('vosi:available')

            # remove available from data dict
            data.pop('available', None)

            # add possible optional nodes:
            for key in data.keys():
                xml.startElement('vosi'+key, {})
                xml.characters(smart_unicode(data[key]))
                xml.endElement('vosi'+key)

            xml.endElement('vosi:availability')

            xml.endDocument()

            xml_string = stream.getvalue()


            # make the xml pretty, i.e. use linebreaks and indentation
            # the sax XMLGenerator behind SimpleXMLGenerator does not seem to support this,
            # thus need a library that can do it.
            # TODO: since we use lxml anyway, maybe build the whole xml-tree with lxml.etree!
            # NOTE: This removes any possibly existing comments from the xml output!
            if prettyprint is True:
                parsed = etree.fromstring(xml_string)
                pretty_xml = etree.tostring(parsed, pretty_print=True)
                xml_string = pretty_xml

            return xml_string


class VosiCapabilityRenderer(BaseRenderer):
        """
        Takes capability data (from a queryset) and
        returns an xmlstream for VOSI capabilities/ endpoint
        """

        charset = 'utf-8'

        # namespace declarations
        ns_vosicap = 'http://www.ivoa.net/xml/VOSICapabilities/v1.0'
        ns_vs = 'http://www.ivoa.net/xml/VODataService/v1.1'
        ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        ns_vr = "http://www.ivoa.net/xml/VOResource/v1.0"
        version = '1.1'

        comment = "<!--\n"\
                + " !  Generated using Django with SimplerXMLGenerator\n"\
                + " !  at "+str(timezone.now())+"\n"\
                + " !-->\n"

        def render(self, capabilities, prettyprint=False):
            """
            parameters:
              capabilities = queryset of voresource_capabilities
              prettyprint = flag for pretty printing the xml output (including whitespace and linebreaks)
            """

            stream = StringIO()
            xml = SimplerXMLGenerator(stream, self.charset)

            xml.startDocument()

            # add a comment
            xml._write(self.comment)

            # add namespace definitions
            nsattrs = {}
            nsattrs['version'] = self.version
            #nsattrs['encoding'] = charser
            nsattrs['xmlns:vosi'] = self.ns_vosicap
            nsattrs['xmlns:xsi'] = self.ns_xsi
            nsattrs['xmlns:vs'] = self.ns_vs
            nsattrs['xmlns:vr'] = self.ns_vr

            # add root node
            xml.startElement('vosi:capabilities', nsattrs)

            # Add all the capabilities, including those for VOSI endpoint,
            # extract them from the database using the provided queryset.
            # The following lookup is not efficient, since there is a database
            # call for each object, it would be more efficient to get a list of
            # all capabilities, interfaces and accessurls and then match them here.
            for capability in capabilities:
                attrs = {}
                if capability.standardID:
                    attrs['standardID'] = str(capability.standardID)
                xml.startElement('capability', attrs)

                interfaces = capability.voresource_interface_set.all()
                for interface in interfaces:
                    attrs = {}
                    if interface.type:
                        attrs['xsi:type'] = interface.type
                    xml.startElement('interface', attrs)

                    accessurls = interface.voresource_accessurl_set.all()
                    for accessurl in accessurls:
                        attrs = {}
                        attrs['use'] = accessurl.use  # throw error, if its not there?
                        xml.startElement('accessURL', attrs)
                        xml.characters(smart_unicode(accessurl.url))
                        xml.endElement('accessURL')

                    xml.endElement('interface')

                xml.endElement('capability')

            xml.endElement('vosi:capabilities')

            xml.endDocument()

            xml_string = stream.getvalue()


            # make the xml pretty, i.e. use linebreaks and indentation
            # the sax XMLGenerator behind SimpleXMLGenerator does not seem to support this,
            # thus need a library that can do it.
            # TODO: since we use lxml anyway, maybe build the whole xml-tree with lxml.etree!
            # NOTE: This removes any possibly existing comments from the xml output!
            if prettyprint is True:
                parsed = etree.fromstring(xml_string)
                pretty_xml = etree.tostring(parsed, pretty_print=True)
                xml_string = pretty_xml

            return xml_string
