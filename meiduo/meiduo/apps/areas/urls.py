from django.conf.urls import url

from areas.views import AreaViewSet, AreasViewSet

urlpatterns = [
    url(r"^areas/$", AreaViewSet.as_view()),
    url(r"^areas/(?P<pk>\d+)/$", AreasViewSet.as_view()),
]
