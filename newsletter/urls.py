from django.conf.urls.defaults import *

urlpatterns = patterns('newsletter.views',
    url(r'^(?P<pk>\d+)/$', 'detail', name='newsletter'),
    url(r'^unsubscribe/(\w+)/(.+)/$', 'unsubscribe', name='unsubscribe'),
)
