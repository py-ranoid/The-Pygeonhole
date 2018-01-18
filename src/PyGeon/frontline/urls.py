from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^allevents/', views.ListEventsView.as_view()),
    url(r'^all/', views.EventListView.as_view()),
]
