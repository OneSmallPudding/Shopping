import base64
import pickle

from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serializers import CartSerialzers, CartSKUSerializer, CartDeleteSerialzers, CartSelectionSerialzers
from goods.models import SKU


class CartsView(APIView):
    '''购物车的增删改查'''

    # 对前段发送的ｔｏｋｅｎ数据时会进行验证
    def perform_authentication(self, request):
        pass

    def post(self, request):
        # 获取数据
        data = request.data
        # 进行序列化验证
        ser = CartSerialzers(data=data)
        ser.is_valid()
        # 序列话的数据
        data = ser.validated_data
        sku_id = data["sku_id"]
        count = data["count"]
        selected = data["selected"]
        # 判断用户是否存在
        try:
            user = request.user
            # 用户登陆
        except:
            # 用户没登录
            user = None
        if user:
            from django_redis import get_redis_connection
            conn = get_redis_connection("carts")
            conn.hincrby("cart_%s" % user.id, sku_id, count)
            if selected:
                conn.sadd("cart_sele_%s" % user.id, sku_id)
            return Response({'message': 'ok'})
        cart = request.COOKIES.get("cart_cookie", None)
        if cart:
            cart = pickle.loads(base64.b64decode(cart))
        else:
            cart = {}
        if sku_id in cart.keys():
            count += cart[sku_id]["count"]

        cart[sku_id] = {
            "count": count,
            'selected': selected
        }
        # '构建相应对象设置加密的ｃｏｏｋｉｅ
        resp = Response({'message': 'ok'})
        cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
        resp.set_cookie("cart_cookie", cart_cookie, max_age=30000000)
        return resp

    def get(self, request):
        # 判断用户是否登陆
        try:
            user = request.user
        except:
            user = None
        if user:
            # 取出数据
            from django_redis import get_redis_connection
            conn = get_redis_connection("carts")
            redis_cart = conn.hgetall("cart_%s" % user.id)
            # cart:{1:{}}
            redis_list = conn.smembers("cart_sele_%s" % user.id)
            cart = {}
            for sku_id, count in redis_cart.items():
                cart[int(sku_id)] = {
                    "count": int(count),
                    "selected": sku_id in redis_list
                }
        else:

            cart_cookie = request.COOKIES.get("cart_cookie")
            if not cart_cookie:
                cart = {}
            else:
                cart = pickle.loads(base64.b64decode(cart_cookie))
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        serializer = CartSKUSerializer(skus, many=True)
        return Response(serializer.data)

        # 返回

    def put(self, request):
        # 获取数据
        data = request.data
        # 进行序列化验证
        ser = CartSerialzers(data=data)
        ser.is_valid()
        # 序列话的数据
        data = ser.data
        sku_id = data["sku_id"]
        count = data["count"]
        selected = data["selected"]
        # 判断用户是否存在
        try:
            user = request.user
            # 用户登陆
        except:
            # 用户没登录
            user = None
        if user:
            from django_redis import get_redis_connection
            conn = get_redis_connection("carts")
            conn.hset("cart_%s" % user.id, sku_id, count)
            if selected:
                conn.sadd("cart_sele_%s" % user.id, sku_id)
            else:
                conn.srem("cart_sele_%s" % user.id, sku_id)
            return Response(ser.data)
        cart = request.COOKIES.get("cart_cookie", None)
        if cart:
            cart = pickle.loads(base64.b64decode(cart))
        else:
            cart = {}

        cart[sku_id] = {
            "count": count,
            'selected': selected
        }
        # '构建相应对象设置加密的ｃｏｏｋｉｅ
        resp = Response(ser.data)
        cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
        resp.set_cookie("cart_cookie", cart_cookie, max_age=3000)
        return resp

    def delete(self, request):
        # 获取数据
        data = request.data
        # 进行序列化验证
        ser = CartDeleteSerialzers(data=data)
        ser.is_valid()
        # 序列话的数据
        data = ser.validated_data
        sku_id = data["sku_id"]

        # 判断用户是否存在
        try:
            user = request.user
            # 用户登陆
        except:
            # 用户没登录
            user = None
        if user:
            from django_redis import get_redis_connection
            conn = get_redis_connection("carts")
            conn.hdel("cart_%s" % user.id, sku_id)

            conn.srem("cart_sele_%s" % user.id, sku_id)
            return Response({'message': 'ok'})
        cart = request.COOKIES.get("cart_cookie", None)
        if cart:
            cart = pickle.loads(base64.b64decode(cart))
        else:
            cart = {}
        if sku_id in cart.keys():
            del cart[sku_id]
            # '构建相应对象设置加密的ｃｏｏｋｉｅ
        resp = Response({'message': 'ok'})
        cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
        resp.set_cookie("cart_cookie", cart_cookie, max_age=3000)
        return resp


class CartSelectionView(APIView):
    '''购物车的全选'''

    # 对前段发送的ｔｏｋｅｎ数据时会进行验证
    def perform_authentication(self, request):
        pass

    def put(self, request):
        # 获取数据
        data = request.data
        # 进行序列化验证
        ser = CartSelectionSerialzers(data=data)
        ser.is_valid()
        # 序列话的数据
        data = ser.data
        selected = data["selected"]
        # 判断用户是否存在
        try:
            user = request.user
            # 用户登陆
        except:
            # 用户没登录
            user = None
        if user:
            from django_redis import get_redis_connection
            conn = get_redis_connection("carts")
            sku_ids = conn.hkeys('cart_%s' % user.id)
            if selected:
                conn.sadd("cart_sele_%s" % user.id, *sku_ids)
            else:
                conn.srem("cart_sele_%s" % user.id, *sku_ids)
            return Response(ser.data)
        cart = request.COOKIES.get("cart_cookie", None)
        if cart:
            cart = pickle.loads(base64.b64decode(cart))
        else:
            cart = {}
        for sku_id in cart.keys():
            cart[sku_id]['selected'] = selected

        # '构建相应对象设置加密的ｃｏｏｋｉｅ
        resp = Response({'message': 'ok'})
        cart_cookie = base64.b64encode(pickle.dumps(cart)).decode()
        resp.set_cookie("cart_cookie", cart_cookie, max_age=3000)
        return resp
