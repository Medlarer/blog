__author__ = 'Arai'
from django.conf.urls import url,include

from blog import  settings

from app01 import views
urlpatterns = [
    url(r'^backend/$', views.backendIndex),
    url(r'^commentTree/(?P<article_id>\d+)', views.commentTree),
    url(r'^backend/addArticle', views.addArticle),
    url(r'^comment', views.comment),
    url(r'^up_down', views.up_down),
    url(r'^down_up', views.down_up),
    url(r'^(?P<username>.*)/(?P<condition>cate|tag|date)/(?P<para>.*)', views.homeSite),
    url(r'^(?P<username>.*)/articles/(?P<article_id>\d+)', views.article_detail),
    url(r'^(?P<username>.*)/', views.homeSite,name="aaa"),

]
