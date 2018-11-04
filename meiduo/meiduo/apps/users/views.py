from random import randint

from django.conf import settings
from django.shortcuts import render
# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, ListCreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from celery_tasks.sms.tasks import send_sms_code
from users.models import User, Address
from users.serializers import UserSerialziers, UserDetailSerializer, EmailSerializer, UserAddressSerializer


class SMSCodeView(APIView):
    def get(self, request, mobile):
        # 获取链接
        conn = get_redis_connection("session1")
        # 控制发送频率
        flag = conn.get("sms_flag_%s" % mobile)
        if flag:
            return Response({"errors": "发送频发"})
        # 生成短信验证码
        sms_code = "%06d" % randint(0, 999999)
        print(sms_code)
        # 保存验证吗
        pl = conn.pipeline()
        pl.setex("sms_%s" % mobile, 300, sms_code)
        pl.setex("sms_flag_%s" % mobile, 5, 1)
        pl.execute()  # 传递指令  写入redis
        # 发送短信验证
        send_sms_code.delay(mobile, sms_code, 1)
        resp = Response({'message': 'ok'})
        resp.set_cookie("ishelp", "gogogog", 1000)
        # 返回结果
        return resp


class UserNameCountView(APIView):
    '''判断用户是否存在'''

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return Response({"count": count})


class MobileCountView(APIView):
    '''判断手机号是否存在'''

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return Response({"count": count})


class UserView(CreateAPIView):
    '''用户注册'''
    serializer_class = UserSerialziers


class UserDetailView(RetrieveAPIView):
    '''用户详情'''
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    '''用户邮箱绑定，发送邮件'''
    serializer_class = EmailSerializer

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    '''验证邮箱'''

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"errors": "token过期"})
        from itsdangerous import TimedJSONWebSignatureSerializer as tjs
        tjs = tjs(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(token)
        except:
            return Response({"errors": "token不正确"})
        id = data["id"]
        try:
            user = User.objects.get(id=id)
        except:
            return Response({"errors": "ｔｏｎｋｅｎ数据不对"})
        if not user:
            return Response({"errors": "无效"})
        user.email_active = True
        user.save()
        return Response({"message": "ok"})


class AddressViewSet(ListCreateAPIView, UpdateAPIView):
    '''用户收货地址管理'''
    serializer_class = UserAddressSerializer

    def get(self, request, *args, **kwargs):
        query_set = self.get_queryset()
        serializer = UserAddressSerializer(query_set, many=True)
        default_address_id = request.user.default_address_id
        return Response({"default_address_id": default_address_id, "address": serializer.data})

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(user=user, is_deleted=False)

    def delete(self, request, pk):
        address = Address.objects.get(pk=pk)
        address.is_deleted = True
        address.save()
        return Response({"errmsg": "ok"})


class StatusView(APIView):
    '''默认地址'''

    def put(self, requset, pk):
        user = requset.user
        user.default_address_id = pk
        user.save()
        address = Address.objects.get(pk=pk)
        ser = UserAddressSerializer(address)
        return Response(ser.data)
