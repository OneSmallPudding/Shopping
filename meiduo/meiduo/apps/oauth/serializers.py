import re

from django.conf import settings
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser
from users.models import User


class QQAuthUserSerializer(serializers.ModelSerializer):
    sms_code = serializers.CharField(max_length=6, write_only=True)
    access_token = serializers.CharField(write_only=True)
    user_id = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)
    mobile = serializers.CharField(max_length=11)

    class Meta:
        model = User
        fields = ['mobile', 'password', 'sms_code', 'access_token', 'username', 'token', 'user_id', 'id']
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
                'read_only': True,
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'max_length': '名字过长',
                    'min_length': '名字过短'
                }
            },
        }

    def validate_mobile(self, valate):
        if not re.match(r"1[3-9]\d{9}", valate):
            raise serializers.ValidationError("手机号格式不对")
        return valate

    def validate(self, attrs):
        from itsdangerous import TimedJSONWebSignatureSerializer as tjs
        tjs = tjs(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(attrs["access_token"])
        except:
            raise serializers.ValidationError("openid不对")
        open_id = data["openid"]
        attrs["open_id"] = open_id
        # 验证短信验证码
        # 建立缓存redis连接
        conn = get_redis_connection('session1')

        # 取出真实验证码   bytes
        real_sms = conn.get('sms_%s' % attrs['mobile'])

        # 判断是否能取出值
        if not real_sms:
            raise serializers.ValidationError('短信验证码已过期')

        # 验证码比对
        if attrs['sms_code'] != real_sms.decode():
            raise serializers.ValidationError('短信验证码不一致')
        # 判断用户是否绑定
        try:
            user = User.objects.get(mobile=attrs["mobile"])
        except:
            # 用户没有注册
            return attrs
        if user.check_password(attrs["password"]):
            raise serializers.ValidationError("密码错误")
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.get("user", None)
        if not user:
            user = User.objects.create_user(username=validated_data['mobile'], password=validated_data['password'],
                                            mobile=validated_data['mobile'], )
        # 将用户绑定openid
        OAuthQQUser.objects.create(
            openid=validated_data['open_id'],
            user=user
        )
        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 用户对象额外添加token属性
        user.token = token
        user.user_id = user.id
        return user
