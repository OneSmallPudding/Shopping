from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser
from oauth.serializers import QQAuthUserSerializer


class QQAuthURLView(APIView):
    '''提供ｑｑ登陆的页面网址'''

    def get(self, request):
        state = request.query_params.get("state")
        if not state:
            state = "/"
        # 获取ｑｑ对象
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI, state=state)
        login_url = qq.get_qq_url()
        print(login_url)

        return Response({"login_url": login_url})


class QQAuthUserView(CreateAPIView):
    '''生产ｏｐｅｎｉｄ和绑定用户'''
    serializer_class = QQAuthUserSerializer

    def get(self, request):
        # 获取ｃｏｄｅ
        code = request.query_params.get("code")
        if not code:
            return Response({"errors": "没有ｃｏｄｅ"})

        # 得到ｏｐｅｎｉｄ
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)

        access_token = oauth.get_access_token(code)
        openid = oauth.get_open_id(access_token)
        # 通过ｏｐｅｎｉｄ查询是否关系表有用户
        try:
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except:
            # 用户没绑定
            from itsdangerous import TimedJSONWebSignatureSerializer as tjs
            tjs = tjs(settings.SECRET_KEY, 300)
            data = tjs.dumps({"openid": openid})
            return Response({"access_token": data})
        else:
            # 用户绑定过
            user = qq_user.user
            # 生成ｔｏｋｅｎ
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Response({
                "token": token,
                "user_id": user.id,
                "username": user.username
            })
