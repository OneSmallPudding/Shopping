from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView

from areas.models import Area
from areas.serializers import AreaSerializer


class AreaViewSet(ListAPIView):
    queryset = Area.objects.filter(parent=None)
    serializer_class = AreaSerializer


class AreasViewSet(ListAPIView):
    serializer_class = AreaSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Area.objects.filter(parent_id=pk)
