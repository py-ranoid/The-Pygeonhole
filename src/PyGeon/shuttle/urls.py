from django.conf.urls import url
from shuttle.views import Bus, Terminal

urlpatterns = [
    url(r'^bus/',  Bus.as_view()),
    url(r'^terminal/', Terminal.as_view()),
]
