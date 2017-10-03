from django.conf.urls import url, include

from rest_framework import routers

from . import views
import vosi.views
import vosi.urls

app_name = 'prov_vo'

# add automatically created urls:
router = routers.DefaultRouter()
router.register(r'activities', views.ActivityViewSet)
router.register(r'entities', views.EntityViewSet)
router.register(r'agents', views.AgentViewSet)
router.register(r'used', views.UsedViewSet)
router.register(r'wasgeneratedby', views.WasGeneratedByViewSet)
router.register(r'wasassociatedwith', views.WasAssociatedWithViewSet)
router.register(r'wasattributedto', views.WasAttributedToViewSet)
router.register(r'hadmember', views.HadMemberViewSet)
router.register(r'wasderivedfrom', views.WasDerivedFromViewSet)
router.register(r'collection', views.CollectionViewSet)

urlpatterns = [
    # index view:
    url(r'^$', views.IndexView.as_view(), name='index'),

    # include automatic rest api urls for models
    # do NOT use a namespace here, because cannot have nested namespaces (prov_vo:api:activites-list won't work)
    url(r'^api/', include(router.urls)),

    # provn of everything:
    url(r'^allprov/(?P<format>[a-zA-Z-]+)$', views.allprov, name='allprov'),
    url(r'^prettyprovn/$', views.prettyprovn, name='prettyprovn'),

    # provdal form
    url(r'^provdal/$', views.provdal, name='provdal'),
    url(r'^provdalform/$', views.provdal_form, name='provdal_form'),
    # vosi endpoints required by dali: capabilities (must be sibling to provdal, Sec. 2 of DALI), availability
    url(r'^availability/$', vosi.views.availability, name='vosi_availability'),
    url(r'^capabilities/$', vosi.views.capabilities, name='vosi_capabilities'),

    # graph overviews
    url(r'^graph/$', views.graph, name='graph'),
    url(r'^graph/graphjson$', views.fullgraphjson, name='graphjson'),

]
