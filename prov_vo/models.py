from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.http import JsonResponse

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
    ('prov:Collection', 'prov:Collection'),
    ('voprov:dataSet', 'voprov:catalog'),
)

#DATA_TYPE_CHOICES = (
#)

AGENT_TYPE_CHOICES = (
    ('voprov:Project','voprov:Project'),
    ('prov:Person','prov:Person'),
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

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Entity(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128, null=True) # human readable label
    type = models.CharField(max_length=128, null=True, choices=ENTITY_TYPE_CHOICES) # types of entities: single entity, dataset
    annotation = models.CharField(max_length=1024, null=True, blank=True)
    rights = models.CharField(max_length=128, null=True, blank=True)
    dataType= models.CharField(max_length=128, null=True, blank=True)
    storageLocation = models.CharField('storage location', max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Agent(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    name = models.CharField(max_length=128, null=True) # human readable label, firstname + lastname
    type = models.CharField(max_length=128, null=True, choices=AGENT_TYPE_CHOICES) # types of entities: single entity, dataset
    annotation = models.CharField(max_length=1024, null=True, blank=True)
    email = models.CharField(max_length=128, null=True, blank=True)

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


# VOSI resources
# ==============
ACCESS_URL_USE_CHOICES = (
    ('full', 'full'),
    ('base', 'base'),
    ('dir', 'dir'),
)


@python_2_unicode_compatible
class AvailabilityOption(models.Model):
    id = models.IntegerField(primary_key=True)
    available = models.BooleanField(help_text="True if the service is available, else false")
    note = models.CharField(max_length=256, blank=True, null=True, help_text="A status message")
    #upSince =
    #downAt =
    #backAt =
    #enabled = models.BooleanField(help_text="Indicate if this status active or not")

    def __str__(self):
        return self.id
class Availability(models.Model):
    enabled = models.ForeignKey(AvailabilityOption, on_delete=models.CASCADE)


@python_2_unicode_compatible
class VOResource_Capability(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=256, blank=True, null=True)  # use choices?
    standardID = models.CharField(max_length=256, blank=True, null=True)  # use choices?
    description = models.CharField(max_length=1024, blank=True, null=True)
    # validationLevel [0..*] -- ignore here

    def __str__(self):
        return self.id


@python_2_unicode_compatible
class VOResource_Interface(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=256, default="vr:WebBrowser")  # use predefined choices here?
    capability = models.ForeignKey(VOResource_Capability, on_delete=models.CASCADE)
    version = models.CharField(max_length=256, blank=True, null=True, default="1.0")
    role = models.CharField(max_length=1024, blank=True, null=True)  # use choices?
    # securityMethod [0..*] -- ignore here

    def __str__(self):
        return self.id


@python_2_unicode_compatible
class VOResource_AccessURL(models.Model):
    id = models.AutoField(primary_key=True)
    interface = models.ForeignKey(VOResource_Interface, on_delete=models.CASCADE)
    url = models.CharField(max_length=1024)
    use = models.CharField(max_length=256, default="full", choices=ACCESS_URL_USE_CHOICES)

    def __str__(self):
        return self.id
