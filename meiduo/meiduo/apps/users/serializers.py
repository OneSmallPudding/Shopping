import re

from django.conf import settings
from django.core.mail import send_mail
from django_redis import get_redis_connection
from rest_framework import serializers

from celery_tasks.email.tasks import send_email
from users.models import User


class UserSerialziers(serializers.ModelSerializer):
    # 指明字段
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password', 'password2', 'sms_code', 'allow', "token"]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
                'error_messages': {
                    'max_length': '密码过长'
                }
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'max_length': '名字过长'
                }
            },
        }

    def validate_mobile(self, value):
        if not re.match(r"^1[3-9]\d{9}$", value):
            raise serializers.ValidationError("手机号格式不正确")
        return value

    def validate_allow(self, value):
        if value != "true":
            raise serializers.ValidationError("没有勾选协议")
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError("密码不一致")
        conn = get_redis_connection("session1")
        real_sms = conn.get("sms_%s" % attrs.get("mobile"))
        if not real_sms:
            raise serializers.ValidationError("验证码过期")
        if attrs.get("sms_code") != real_sms.decode():
            raise serializers.ValidationError("验证码不对")
        return attrs

    def create(self, validated_data):
        print(validated_data)
        del validated_data["password2"]
        del validated_data["allow"]
        del validated_data["sms_code"]
        print(validated_data)

        user = User.objects.create_user(username=validated_data['username'], mobile=validated_data['mobile'],
                                        password=validated_data['password'])
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    '''用户详情页'''

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', "email", "email_active"]


class EmailSerializer(serializers.ModelSerializer):
    '''邮箱修改'''

    class Meta:
        model = User
        fields = ["email"]

    def update(self, instance, validated_data):
        from itsdangerous import TimedJSONWebSignatureSerializer as tjs
        tjs = tjs(settings.SECRET_KEY, 300)
        token = tjs.dumps({"id": instance.id}).decode()
        to_email = validated_data["email"]
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        send_email.delay(to_email, verify_url)
        # send_mail('biaoti', 'yanzheng', settings.EMAIL_FROM, [validated_data['email']])
        super().update(instance, validated_data)
        return instance
