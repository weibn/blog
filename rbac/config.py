from app01 import views
from app02 import views2
from django.conf.urls import url
from django.contrib import admin

VALID_URL = [
    'login.html',
    'reg.html$',
    '^all/(?P<type_id>\d+)/',
    '^check_code/',
    '^up_img/',

    '^seek/',

    '^logout/',
    '^add_up/',
    '^comment/',
    '^check_comment/',
    '^del_comment/',
    '^control.html$',
    '^upload_img.html$',
    '^add_article.html$',
    '^article_manage/(?P<article_type_id>\d+)-(?P<category_id>\d+)-(?P<tags__nid>\d+).html$',
    '^(?P<site>\w+)/p/(?P<nid>\d+).html$',
    '^(?P<site>\w+)/(?P<family>\w+)/(?P<nid>\d+-?\d*).html$',
    'index.html',
    '^(?P<site>\w+).html$',
]