import os

from django.conf import settings
from rest_framework import status

from rest_framework.response import Response
from rest_framework.views import APIView
from alipay import AliPay

from orders.models import OrderInfo
from payment.models import Payment


class PaymentView(APIView):
    '''支付'''

    def get(self, request, order_id):
        # 获取订单编号，验证有效性
        try:
            order = OrderInfo.objects.get(user=request.user, order_id=order_id, pay_method=2, status=1)
        except:
            return Response({'errors': '无效的订单'}, status=401)
        # 支付初始化
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_public_key.pem"),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多啊",
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return Response({"alipay_url": alipay_url})

class PaymentStatusView(APIView):
    def put(self,request):
        data =request.query_params.dict()
        signature = data.pop("sign",None)
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_public_key.pem"),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        result = alipay.verify(data,signature)
        if result:
            order_id = data.get("out_trade_no")
            trade_id = data.get('trade_no')
            # 关联订单号和交易流水号
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 更新支付状态
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
            return Response({'trade_id': trade_id})
        else:
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)