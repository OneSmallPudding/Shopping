
from django.conf.urls import url

from orders.views import OrderView

urlpatterns = [
    url(r'^orders/settlement/$', OrderView.as_view()),
]
