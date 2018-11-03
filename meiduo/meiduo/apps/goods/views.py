from django.shortcuts import render

# Create your views here.
from drf_haystack.viewsets import HaystackViewSet

from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU, GoodsCategory
from goods.serializers import SKUSerializer, SKUIndexSerializer, UserGoodsHistorySerializer
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
    '''面包屑导航'''

    def get(self, request, pk):
        cat3 = GoodsCategory.objects.get(pk=pk)
        cat2 = cat3.parent
        cat1 = cat2.parent
        return Response({
            'cat1': cat1.name,
            'cat2': cat2.name,
            'cat3': cat3.name,
        })


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer
    pagination_class = StandardResultsSetPagination


class UserGoodsHistoryView(ListCreateAPIView):
    '''保存和获取用户浏览的商品信息'''

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserGoodsHistorySerializer
        return SKUSerializer

    def get_queryset(self):
        user = self.request.user
        from django_redis import get_redis_connection
        conn = get_redis_connection("history")
        data_list = conn.lrange("history_%s" % user.id, 0, 5)
        return SKU.objects.filter(id__in=data_list)
