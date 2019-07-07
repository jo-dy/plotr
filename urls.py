from django.conf.urls import patterns, url

from plotr import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^(?P<dataset_id>[\dA-Za-z]+)/tabular/$', views.tabular, name='tabular'),
    url(r'^(?P<dataset_id>[\dA-Za-z]+)/v/(?P<viz_type>[a-z]+)/(?P<var_string>.*)/i/$', views.viz_image, name='viz_image'),
    url(r'^(?P<dataset_id>[\dA-Za-z]+)/v/(?P<viz_type>[a-z]+)/(?P<var_string>.*)/$', views.viz_page, name='viz_page'),
    url(r'^(?P<dataset_id>[\dA-Za-z]+)/v/(?P<viz_type>[a-z]+)/$', views.viz_specify_var, name='viz_specify_var'),
    url(r'^error/500/$', views.trigger_http_500, name='trigger_http_500'),
    url(r'^error/404/$', views.trigger_http_404, name='trigger_http_404'),
    url(r'^(?P<dataset_id>[\dA-Za-z]+)/$', views.summary, name='summary'),    
)