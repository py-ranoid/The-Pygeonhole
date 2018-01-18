from django.conf.urls import url
from views import HackathonCreate, DetailsView

urlpatterns = [
    url(r'^hack/', HackathonCreate.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', DetailsView.as_view(), name='details'),
]
