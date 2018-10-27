from django.conf.urls import url

from oauth.views import QQAuthURLView, QQAuthUserView

urlpatterns = [
    url(r"^qq/authorization/$", QQAuthURLView.as_view()),
    url(r"^qq/user/$", QQAuthUserView.as_view())
]
