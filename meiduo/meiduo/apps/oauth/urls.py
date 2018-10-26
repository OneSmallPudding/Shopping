from django.conf.urls import url

from oauth.views import QQAuthURLView

urlpatterns = [
    url(r"^qq/authorization/$", QQAuthURLView.as_view())
]
