"""exp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.shortcuts import redirect
from TDS.overwatch import job, CPjob, Meetupjob
from grappelli import dashboard
from django.conf.urls.static import static
from django.conf import settings
from home.views import Hello, feedReceive

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^app/', include('prime.urls')),
    url(r'^shuttle/', include('shuttle.urls')),
    url(r'^data/', include('warehouse.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    # url(r'^grap/', dashboard,
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls',
                                    'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^frontline/', include('frontline.urls')),
    url(r'^home/', include('home.urls')),
    url(r'^$', Hello.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Meetupjob()
# job()
