from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView


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
        return Response({"login_url": login_url})
