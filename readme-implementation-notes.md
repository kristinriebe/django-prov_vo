
## General remarks
Provenance classes can be implemented directly as Django model classes.
When using Django RestFramework, one can easily get an API for retrieving
all activities/entities etc., getting details for one of them etc.
Updating an object or adding a new one via the REST API is not implemented (yet).

## Tracking provenance
Provenance for an entity, activity or agent can be tracked backwards via the different relations.
Provenance tracking is done recursively, because:
    * It is unknown, how many steps one needs to go backwards.
    * There may be loops, i.e. one node of the provenance graph may be visited multiple times.

I defined three main functions `track_entity`, `track_activity` and `track_agent` to take care of finding relations for an entity/activity/agent and following the linked entities/activities further. There is no need to follow agents (unless a special option is set to true).

I decided to return **each node only once**, i.e I always check if a node was
already visited, and if so, I stop tracking that path any further (because I did it already). This is especially important if circles can occur, because then the maximum recursion depth could be quickly reached if always following each node, even multiple times.

## Prov-DAL
The Prov-DAL interface is implemented at `/prov_vo/provdal/` and can be used to
retrieve provenance records for one or more entities, activities or even agents based on their ids. A form is available at `/prov_vo/provdalform` for convenience to fill out the available parameters as described in the IVOA Provenance Working Draft.

If a user asks for the provenance record of an entity or activity with option "DEPTH=1", then only one relation until the next node is tracked, independent of the type of relation.

The form currently does not support it, but it is possible to use the ID-parameter multiple times in a request to retrieve the provenance of more than one entity, activity or agent at once.

Currently, the Prov-DAL endpoint only supports PROV-N and PROV-JSON format. By choosing FORMAT=GRAPH instead, one can also get a webpage with a graphical representation of the retrieved provenance description using Javascript.

The parameter MODEL is used to distinguish between serializing the data according to the IVOA or W3C Provenance Data Model. This is now also an optional parameter in the IVOA ProvenanceDM standard draft.


## Implementing Collection
Entities that are collections and can have members are stored as Collection, 
which is an inherited class from Entity. So far, the attributes are not different, thus when serializing/displaying a collection, it has the same attributes as an entity.

Also, when loading collection data into the database, collections are stored in the entity-table and only additionally linked from the collection-table. I.e. when looking for an entity or a collection, it's still enough to do the lookup with the entity-table. But if one needs to make sure that something is a collection, then one should look it up in the collection-table.

In W3C serialization, Collections are Entities with type "prov:collection". In IVOA we can serialize them explicitly as collections.
(Having the same attributes as entity + hadMember relationship.)

Advantage of collection as class:
- in HadMember, the collection-attribute must link to a collection, which is a straight-forward constraint if collection is an extra class
- can check very clearly, if something is a collection or not (even if metadata are incomplete) by checking if the entity occurs in Collection table as well
- if additional attributes are needed, then I need the extra class

Advantage of collection as entity with type 'prov:collection':
- less models (classes) need to be implemented, i.e. also less serializers etc.
- faster, because additional lookup in Colleciton table not needed
    + if I want to know the type, I just look up the attribute type;
    + => no additional database request needed

Thus, for now, I use only the type 'prov:collection' to mark collection entities.


## Serialization
I tested the (W3C) serializations by uploading them into Southampton's ProvStore and ProvValidator. Thus I realized many minor issues that I had not been aware before, so I summarize them here.

### Trouble with qualified attributes (prov:type etc.)
The W3C serializations (for PROV-N, PROV-JSON) expect qualified names for attributes, i.e. a namespace must be given for each key, e.g. "prov:label", "prov:type" etc. This is not supported in serializers
from Django RestFramework. I therefore have written a CustomCharField class
that accepts an additional keyword argument `custom_field_name`. Here any
string can be given. This additional attribute is then used by a custom
serializer class (NonNullCustomSerializer) to replace the `field_name`
in the `to_representation` method.

**Idea**: Actually, one could also implement full namespace support and add a "namespace" attribute instead. But the `custom_field_name` implementation
is sufficient for now, especially since I know exactly which namespaces I need
to support.

### Do not serialize null-fields
I have defined a custom basic serializer class, that inherits from ModelSerializer and just overrides the "to_representation"
method. This is the method which converts to the native data object
(an ordered dictionary).

I have implemented 2 important changes:

* skip fields that are not set (Null/None)
* set `field_name` to `custom_field_name` (if exists and not None)


### Blank namespace for identifiers in PROV-N not valid?
When using a blank namespace for relationship ids when rendering PROV-N, the
resulting provn-file cannot be uploaded to ProvStore or ProvValidator (see https://provenance.ecs.soton.ac.uk/validator/view/translator.html). It will fail with

"java.lang.NullPointerException: Namespace.stringToQualifiedName(: Null namespace for _"

Using no namespace is also not allowed, since ids must be qualified names. Therefore I just use namespace "r" for now.


### No explicit datatypes for PROV literals (values)
This is done in PROV-JSON using the construct:

```
"number": {
        "$": "10",
        "type": "xsd:Integer"
}
```

and similar (in PROV-N, the datatypes are marked using %% after the value). The default type is "xsd:string", so if the values are given like this:

```
"number": "10"
```

then a string datatype is assumed. This is good enough for us now, so I'll just skip explicitly mentioning the datatypes for now.

### IVOA serialization
According to the IVOA Provenance DM requirements, it must be possible to serialize the provenance information into at least one of the W3C formats.
Since we also define additional classes and additional/different attributes in IVOA Provenance DM, we also need a serialization format that can reflect these classes and attributes directly.

If someone intends to use provenance records with W3C-clients/tools, he/she should use a W3C compliant serialization. But then one cannot make use of the additional features.
If someone intends to use provenance records with VO-tools, these VO-tools may digest VO-specific information.

Thus, I wrote VO-variants of the serializers for each model, which more directly map the model attributes and use "voprov" as namespace everywhere.

### W3C serialization of ActivityFlow
Since ActivityFlow and HadStep do not exist in W3C, they have to be represented differently:
* represent each activityFlow as an activity; additional attribute `voprov:votype = 'voprov:activityFlow'`
* represent each hadStep relation as an wasInfluencedBy relation; additional attribute `voprov:votype = 'voprov:hadStep'`

## Issues to be taken care of
* provn serialization needs marker "-" for missing elements, e.g. for time in `used` and `wasGeneratedBy` relationship
* all ids must be qualified (even for relations)
* all attributes must be qualified (even the non-prov attributes)
* `prov:role` is not allowed in wasAttributedTo statements (but it's ok for the others), thus I defined voprov:role for the serialization
* `hadMember` has no id and no optional attributes in W3C (i.e. also no role)

## Validation
use e.g. https://provenance.ecs.soton.ac.uk/validator/view/validator.html
=> works now with my json and provn serialization

https://provenance.ecs.soton.ac.uk/validator/view/translator.html
=> works now as well

Uploading to ProvStore works with the generated PROV-JSON and PROV-N provenance descriptions.

## TODO
* implement PROV-XML and VOTABLE format
* use description-classes
* use collection class in IVOA ProvenanceDM explicitly
* find a better solution for providing a dynamic url for graphjson?
* make use of ProvenanceGraphSerializer for overview graph, observationId form etc. as well
* use different api-root for W3C and IVOA (rest framework)
* fix datetime (UTC)

* finish implementing ActivityFlow:
    - auto-generate wasGeneratedBy and used-relationships? Or insert?
        + (but cannot know, which entities are used outside of act. flow and which not! => Have to assume that they all are important.)
    - graphical view: choose viewLevel, show/hide details inside activityFlow,
        + properly show relations via plan for W3C representation

* implement bundles for grouping provenance records (and also for prov. of prov.) -- could use a new bundle class (model), temporarily create a bundle-thing with list of activities, entities, agents etc. and then create a bundle serializer.
* add prov-namespace in the renderer after all? I.e. serializer just deals with renaming and restructuring, renderer adds namespaces and omits null-fields; it may be better to expose the real underlying data via the REST API,
i.e. using the non-namespaced and not renamed fields.

### To be discussed
* Need additional ActivityCollection for grouping all the individual observations to one? (In addition to ActivityFlow?)

###  At some point later in the future
* maybe use a proper namespace-solution after all? For the serialisation?
* add datatypes ($, type) where needed for json and provn serialization
* convert to Python3


