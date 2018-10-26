import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    '''自定义ｊｗｔ返回结果'''
    return {
        "token": token, "user_id": user.id, "username": user.username
    }


class UsernameMobileAuthBackend(ModelBackend):
    '''对判断进行重写，添加手机号登陆'''

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if re.match(r"^1[3-9]\d{9}$", username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except:
            user = None
        if user and user.check_password(password):
            return user
