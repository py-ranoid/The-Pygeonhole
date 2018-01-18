from django.conf.urls import url
from home.views import Hello, feedReceive
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^landing/', Hello.as_view()),
    url(r'^feedback/', feedReceive )
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
