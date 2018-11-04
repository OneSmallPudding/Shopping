from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView

from areas.models import Area
from areas.serializers import AreaSerializer
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class AreaViewSet(CacheResponseMixin, ListAPIView):
    '''所有的省级信息'''
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer


class AreasViewSet(CacheResponseMixin, ListAPIView):
    '''所有的市区信息'''
    serializer_class = AreaSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Area.objects.filter(parent_id=pk)
