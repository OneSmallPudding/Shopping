from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import OrdersSerializer, SaveOrderSerializer


# class OrderView(ListAPIView):
#     '''获取生成订单'''
#
#     def get_queryset(self):
#         user = self.request.user
#         from django_redis import get_redis_connection
#         conn = get_redis_connection("carts")
#         cart_dict = conn.hgetall('cart_%s' % user.id)
#         sku_ids = conn.smembers('cart_sele_%s' % user.id)
#         cart_count = {}
#         for sku_id, count in cart_dict.items():
#             if sku_id in sku_ids:
#                 cart_count[int(sku_id)] = int(count)
#         skus = SKU.objects.filter(id__in=cart_count.keys())
#         for sku in skus:
#             sku.count = cart_count[sku.id]
#         return skus
#     serializer_class = OrderSerializer
class OrderView(APIView):
    '''获取生成订单'''

    def get(self, request):
        user = request.user
        from django_redis import get_redis_connection
        conn = get_redis_connection("carts")
        cart_dict = conn.hgetall('cart_%s' % user.id)
        sku_ids = conn.smembers('cart_sele_%s' % user.id)
        cart_count = {}
        for sku_id, count in cart_dict.items():
            if sku_id in sku_ids:
                cart_count[int(sku_id)] = int(count)
        skus = SKU.objects.filter(id__in=cart_count.keys())
        for sku in skus:
            sku.count = cart_count[sku.id]
        freight = 10.00
        # freight = Decimal('10.00')
        serializer = OrdersSerializer(skus, many=True)

        return Response({"freight": freight, "skus": serializer.data})


class SaveOrderView(CreateAPIView):
    '''保存订单'''

    serializer_class = SaveOrderSerializer
