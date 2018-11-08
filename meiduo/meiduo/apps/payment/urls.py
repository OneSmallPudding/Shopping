from django.conf.urls import url

from payment.views import PaymentView, PaymentStatusView

urlpatterns = [
    url(r'^orders/(?P<order_id>\d+)/payment/$', PaymentView.as_view()),
    url(r'^payment/status/$', PaymentStatusView.as_view()),
]
