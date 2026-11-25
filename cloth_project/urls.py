"""
URL configuration for cloth_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from cloth_app.sitemap import *
from cloth_app import views
admin.site.site_header="Us Vesta"
admin.site.site_title="Us Vesta"
admin.site.index_title="Wellcome To Us Vesta Portal"
sitemaps={
    'post':TodoSitemap,
    'sinpet':TodoSitemap001,
    "three":TodoSitemap003,
    "four":TodoSitemap004,
    "five":TodoSitemap005,
}

urlpatterns = [
    path('usvesta-crm/', admin.site.urls),
    path('',include("cloth_app.urls")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('robots.txt',include('robots.urls')),
    path('nested_admin/', include('nested_admin.urls')),
    path('accounts/', include('allauth.urls')),  # allauth routes
]

from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
