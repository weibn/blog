"""blogtest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from app01 import views
from app02 import views2

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'login.html$', views.login),
    url(r'reg.html$', views.reg),
    url(r'^all/(?P<type_id>\d+)/', views.index),
    url(r'^check_code/', views.check_code),
    url(r'^up_img/', views.up_img),

    url(r'^seek/', views2.seek),

    url(r'^logout/', views.logout),
    url(r'^add_up/', views.add_up),
    url(r'^comment/', views.comment),
    url(r'^check_comment/', views.check_comment),
    url(r'^del_comment/', views.del_comment),
    url(r'^control.html$', views.control),
    url(r'^upload_img.html$', views.upload_img),
    url(r'^add_article.html$', views.add_article),
    url(r'^article_manage/(?P<article_type_id>\d+)-(?P<category_id>\d+)-(?P<tags__nid>\d+).html$', views.article_manage),


    url(r'^(?P<site>\w+)/p/(?P<nid>\d+).html$', views.page),
    url(r'^(?P<site>\w+)/(?P<family>\w+)/(?P<nid>\d+-?\d*).html$', views.user),
    url(r'^(?P<site>\w+).html$', views.user),

    url(r'index.html', views.index),
    url(r'', views.me),
]
