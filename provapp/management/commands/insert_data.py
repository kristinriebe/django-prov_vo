from django.core.management.base import BaseCommand
from provapp.models import Activity, Entity, Agent, Used, WasGeneratedBy, WasAssociatedWith, HadMember, WasDerivedFrom

# call the class+function below using:
# python manage.py insert_data
class Command(BaseCommand):
    args = ""
    help = "Import initial data for testing the provenance application"

    def _insert_entities(self):
        filename = "0752m38.rvsun.089.nocont.txt"
        name = "0752m38.rvsun.089.*cont*"
#e = Entity(id="rave:"+name, label=name, type="prov:collection", description="SPARV data set for one day and one fibre", status="voprov:restricted", dataType="vorpov:fits", storageLocation="/store/01/RAVE/Processing/DR4/20121220/*089*")

        date = "20121220"
        obstime = "0752m38"
        fibernumber = "089"

        #id, label, type, description, status, dataType, storageLocation
        e = Entity(id="rave:"+name, 
                   label=name, 
                   type="voprov:collection", 
                   description="uncorrelated spectrum, extracted from IRAF-fits for one fibre", 
                   status="voprov:restricted", 
                   dataType="voprov:fits", 
                   storageLocation="/store/01/RAVE/Processing/DR4/"+date+"/"+obstime+".rvsun."+fibernumber+".*.txt"
        )
        e.save()
        self.stdout.write(self.style.SUCCESS('Success? entity: "%s"' % e.id))

        #h = HadMember(id="")
        #w = wasGeneratedBy
        #w = wasDerivedFrom
        #used = ...


    def handle(self, *args, **options):
        self._insert_entities()