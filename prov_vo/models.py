from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.http import JsonResponse
import vosi.models

# choice lists, they are *not* complete
ACTIVITY_TYPE_CHOICES = (
    ('obs:Observation', 'obs:Observation'),
    ('obs:Reduction', 'obs:Reduction'),
    ('obs:Classification', 'obs:Classification'),
    ('obs:Crossmatch', 'obs:Crossmatch'),
    ('calc:ChemicalPipeline', 'calc:ChemicalPipeline'),
    ('calc:Distances', 'calc:Distances'),
    ('other', 'other'),
)

ENTITY_TYPE_CHOICES = (
    ('voprov:Collection', 'voprov:Collection'),
    ('voprov:Entity', 'voprov:Entity'),
)

AGENT_TYPE_CHOICES = (
    ('voprov:Organization','voprov:Organization'),
    ('voprov:Individual','voprov:Individual'),
)

ENTITY_RIGHTS_CHOICES = (
    ('voprov:public', 'voprov:public'),
    ('voprov:secure', 'voprov:secure'),
    ('voprov:propriatary', 'voprov:proprietary')
)

# datatypes from VOTable 1.3 REC:
DATATYPE_CHOICES = (
    ('vo:boolean', 'vo:boolean'),
    ('vo:bit', 'vo:bit'),
    ('vo:unsignedByte', 'vo:unsignedByte'),
    ('vo:short', 'vo:short'),
    ('vo:int', 'vo:int'),
    ('vo:long', 'vo:long'),
    ('vo:char', 'vo:char'),
    ('vo:unicodeChar', 'vo:unicodeChar'),
    ('vo:float', 'vo:float'),
    ('vo:double', 'vo:double'),
    ('vo:floatComplex', 'vo:floatComplex'),
    ('vo:doubleComplex', 'vo:doubleComplex')
)

XTYPE_CHOICES = (
    ('timestamp', 'timestamp'),
    ('position', 'position')
)

# main ProvenanceDM classes:
@python_2_unicode_compatible
class Activity(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128, null=True) # should require this, otherwise do not know what to show!
    type = models.CharField(max_length=128, null=True, choices=ACTIVITY_TYPE_CHOICES)
    annotation = models.CharField(max_length=1024, blank=True, null=True)
    startTime = models.DateTimeField(null=True) # should be: null=False, default=timezone.now())
    endTime = models.DateTimeField(null=True) # should be: null=False, default=timezone.now())
    doculink = models.CharField('documentation link', max_length=512, blank=True, null=True)
    description = models.ForeignKey("ActivityDescription", null=True)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class ActivityDescription(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128, null=True) # should require this, otherwise do not know what to show!
    type = models.CharField(max_length=128, null=True, choices=ACTIVITY_TYPE_CHOICES)
    subtype = models.CharField(max_length=128, blank=True, null=True)
    annotation = models.CharField(max_length=1024, blank=True, null=True)
    doculink = models.CharField('documentation link', max_length=512, blank=True, null=True)
    code = models.CharField(max_length=128, blank=True, null=True)
    version = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Entity(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128, null=True) # human readable label
    type = models.CharField(max_length=128, null=True, choices=ENTITY_TYPE_CHOICES) # types of entities: single entity, dataset
    annotation = models.CharField(max_length=1024, null=True, blank=True)
    rights = models.CharField(max_length=128, null=True, blank=True, choices=ENTITY_RIGHTS_CHOICES)
    description = models.ForeignKey("EntityDescription", null=True)

    # non-standard attributes:
    datatype= models.CharField(max_length=128, null=True, blank=True, choices=DATATYPE_CHOICES)
#    # maybe use obscore_access_format?
    storageLocation = models.CharField('storage location', max_length=1024, null=True, blank=True)
#    # may be use obscore_access_url here? But this is not the same as directory path on a server ...

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class EntityDescription(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128, null=True) # human readable label
    annotation = models.CharField(max_length=1024, null=True, blank=True)
    category = models.CharField(max_length=128, null=True, blank=True)
    doculink = models.CharField('documentation link', max_length=512, blank=True, null=True)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Agent(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128, null=True) # human readable label, firstname + lastname
    type = models.CharField(max_length=128, null=True, choices=AGENT_TYPE_CHOICES) # types of entities: single entity, dataset
    email = models.CharField(max_length=128, null=True, blank=True)
    address = models.CharField(max_length=128, null=True, blank=True)

    # non standard attribute:
    annotation = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.name


# collection classes
@python_2_unicode_compatible
class ActivityFlow(Activity):

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Collection(Entity):

    def __str__(self):
        return self.name


# parameter classes
@python_2_unicode_compatible
class Parameter(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    description = models.ForeignKey("ParameterDescription", null=True)
    value = models.CharField(max_length=128, null=True, blank=True)
    activity = models.ForeignKey(Activity, null=True)

    def __str__(self):
        return self.id

@python_2_unicode_compatible
class ParameterDescription(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128, null=True, blank=True)
    # activityDescription = models.ForeignKey(ActivityDescription, null=True)
    annotation = models.CharField(max_length=512, null=True, blank=True)
    # TODO: should datatype be mandatory?
    datatype = models.CharField(max_length=128, null=True, blank=True, choices=DATATYPE_CHOICES)
    xtype = models.CharField(max_length=128, null=True, blank=True, choices=XTYPE_CHOICES)
    unit = models.CharField(max_length=128, null=True, blank=True)
    ucd = models.CharField(max_length=128, null=True, blank=True)
    utype = models.CharField(max_length=128, null=True, blank=True)
    arraysize = models.IntegerField(null=True, blank=True)
    minval = models.CharField(max_length=128, null=True, blank=True)
    maxval = models.CharField(max_length=128, null=True, blank=True)
    options = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.id


# relation classes
@python_2_unicode_compatible
class Used(models.Model):
    id = models.AutoField(primary_key=True)
    activity = models.ForeignKey(Activity, null=True) #, on_delete=models.CASCADE) # Should be required!
    entity = models.ForeignKey(Entity, null=True) #, on_delete=models.CASCADE) # Should be required!
    time = models.DateTimeField(null=True)
    role = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "id=%s; activity=%s; entity=%s; role=%s" % (str(self.id), self.activity, self.entity, self.role)

@python_2_unicode_compatible
class WasGeneratedBy(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.ForeignKey(Entity, null=True) #, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, null=True) #, on_delete=models.CASCADE)
    time = models.DateTimeField(null=True)
    role = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "id=%s; entity=%s; activity=%s; role=%s" % (str(self.id), self.entity, self.activity, self.role)

@python_2_unicode_compatible
class WasDerivedFrom(models.Model):
    id = models.AutoField(primary_key=True)
    generatedEntity = models.ForeignKey(Entity, null=True)
    usedEntity = models.ForeignKey(Entity, related_name='generatedEntity', null=True) #, on_delete=models.CASCADE)

    def __str__(self):
        return "id=%s; generatedEntity=%s; usedEntity=%s" % (str(self.id), self.generatedEntity, self.usedEntity)

@python_2_unicode_compatible
class WasInformedBy(models.Model):
    id = models.AutoField(primary_key=True)
    informed = models.ForeignKey(Activity, null=True)
    informant = models.ForeignKey(Activity, related_name='informed', null=True)
#    role = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "id=%s; entity=%s; agent=%s; role=%s" % (str(self.id), self.entity, self.agent, self.role)

@python_2_unicode_compatible
class WasAssociatedWith(models.Model):
    id = models.AutoField(primary_key=True)
    activity = models.ForeignKey(Activity, null=True)
    agent = models.ForeignKey(Agent, null=True) #, on_delete=models.CASCADE)
    role = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return "id=%s; activity=%s; agent=%s; role=%s" % (str(self.id), self.activity, self.agent, self.role)

@python_2_unicode_compatible
class WasAttributedTo(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.ForeignKey(Entity, null=True)
    agent = models.ForeignKey(Agent, null=True) #, on_delete=models.CASCADE)
    role = models.CharField(max_length=128, blank=True, null=True)  # not allowed by W3C!!

    def __str__(self):
        return "id=%s; entity=%s; agent=%s; role=%s" % (str(self.id), self.entity, self.agent, self.role)

# collection relations
@python_2_unicode_compatible
class HadMember(models.Model):
    id = models.AutoField(primary_key=True)
    collection = models.ForeignKey(Collection, null=True)  # enforce prov-type: collection
    entity = models.ForeignKey(Entity, related_name='ecollection', null=True) # related_name = 'collection' throws error!

    def __str__(self):
        return "id=%s; collection=%s; entity=%s; role=%s" % (str(self.id), self.collection, self.entity, self.role)

@python_2_unicode_compatible
class HadStep(models.Model):
    id = models.AutoField(primary_key=True)
    activityFlow = models.ForeignKey(ActivityFlow, null=True) #, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, related_name='activityFlow', null=True)

    def __str__(self):
        return "id=%s; activityFlow=%s; activity=%s" % (str(self.id), self.activityFlow, self.activity)
