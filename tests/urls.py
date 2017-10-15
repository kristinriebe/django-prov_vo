from django.conf.urls import url, include

urlpatterns = [
	url(r'^prov_vo/', include('prov_vo.urls', namespace='prov_vo')),
]