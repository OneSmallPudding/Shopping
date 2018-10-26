from rest_framework import serializers
from users.models import User
from django_redis  import get_redis_connection
import re


class UserSerialziers(serializers.ModelSerializer):

    # 显示指明字段

    password2=serializers.CharField(max_length=20,min_length=8,write_only=True)
    sms_code=serializers.CharField(max_length=6,min_length=6,write_only=True)
    allow=serializers.CharField(write_only=True)

    class Meta:
        model=User
        fields = ('id', 'username', 'mobile', 'email', 'password', 'password2', 'sms_code', 'allow')
        extra_kwargs={
            'password':{
                'write_only':True,
                'max_length':20,
                'min_length':8,
                'error_messages':{
                    'max_length':'密码过长'
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

    # 手机号验证
    def validate_mobile(self, value):

        if not re.match(r'^1[3-9]\d{9}$',value):

            raise serializers.ValidationError('手机格式不正确')

        return value

    # 验证选中协议状态
    def validate_allow(self, value):

        if value != 'true':
            raise serializers.ValidationError('协议未选中')

        return value

    def validate(self, attrs):
        # 密码比对
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')

        # 短信验证码判断
        # 建立缓存redis连接
        conn= get_redis_connection('verify')

        # 取出真实验证码   bytes
        real_sms=conn.get('sms_%s'%attrs['mobile'])

        # 判断是否能取出值
        if not real_sms:
            raise serializers.ValidationError('短信验证码已过期')

        # 验证码比对
        if attrs['sms_code'] != real_sms.decode():
            raise serializers.ValidationError('短信验证码不一致')

        return attrs


    def create(self, validated_data):
        print(validated_data)
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        print(validated_data)

        # user=super().create(validated_data)
        # # 自动加密
        # user=User.objects.create_user(username=validated_data['username'],mobile=validated_data['mobile'],password=validated_data['password'])
        # # 手动加密
        user=User.objects.create(username=validated_data['username'],mobile=validated_data['mobile'],password=validated_data['password'])
        user.set_password(validated_data['password'])
        user.save()


        return user




