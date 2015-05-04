from django.conf.urls import patterns, include, url
from django.contrib import admin
from ahp import views

urlpatterns = patterns('',
    url(r'^ahp/', include('ahp.urls')),
    url('', include('ahp.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
