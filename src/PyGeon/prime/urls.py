from django.conf.urls import include, url
from .views import BotView, SheetsPingView
urlpatterns = [url(r'^dcae3db9ad68d046e97d503da41a068aed8663feec28882d94/?$', BotView.as_view()),
               url(r'^sheetsping/?$', SheetsPingView.as_view())]
