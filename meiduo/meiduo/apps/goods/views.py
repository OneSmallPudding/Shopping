from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from goods.models import SKU
from goods.serializers import SKUSerializer
from goods.utils import StandardResultsSetPagination


class SKUListView(ListAPIView):
    '''SKU列表数据'''
    serializer_class = SKUSerializer

    def get_queryset(self):
        pk = self.kwargs["pk"]
        return SKU.objects.filter(category_id=pk)

    pagination_class = StandardResultsSetPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['create_time', 'price', 'sales']
