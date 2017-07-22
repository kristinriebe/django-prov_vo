from django.contrib import admin

# Register your models here.
from .models import Activity, Entity, Agent 
from .models import Used, WasGeneratedBy, HadMember, WasDerivedFrom, WasAssociatedWith, WasAttributedTo

admin.site.register(Activity)
admin.site.register(Entity)
admin.site.register(Agent)

admin.site.register(Used)
admin.site.register(WasGeneratedBy)
admin.site.register(HadMember)
admin.site.register(WasDerivedFrom)
admin.site.register(WasAssociatedWith)
admin.site.register(WasAttributedTo)
