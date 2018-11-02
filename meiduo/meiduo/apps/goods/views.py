from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU, GoodsCategory
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


class GoodCategorieView(APIView):
    def get(self, request, pk):
        cat3 = GoodsCategory.objects.get(pk=pk)
        cat2 = cat3.parent
        cat1 = cat2.parent
        return Response({
            'cat1': cat1.name,
            'cat2': cat2.name,
            'cat3': cat3.name,
        })
