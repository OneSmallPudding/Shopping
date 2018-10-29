from random import randint
from django.shortcuts import render
# Create your views here.
from django_redis import get_redis_connection
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from celery_tasks.sms.tasks import send_sms_code
from users.models import User
from users.serializers import UserSerialziers, UserDetailSerializer, EmailSerializer


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
