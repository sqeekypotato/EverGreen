"""EverGreen URL Configuration

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
from django.conf.urls import url, include

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.urlpatterns import format_suffix_patterns

from core_app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # \
    url(r'^$', views.home, name='home'),
    # \main
    url(r'^main_page/$', views.main_page, name='main_page'),
    # /new_account
    url(r'^new_account/$', views.newAccount, name='new_account'),
    # redirect_details
    # url(r'^redirect_details/$', views.redirect_details, name='redirect_details'),
    # account_details
    url(r'^account_details/$', views.account_details, name='account_details'),
    # tags
    url(r'^tags/$', views.tags, name='tags'),
    # get_tags
    url(r'^get_tag/$', views.get_tag, name='get_tags'),
    # # signup
    url(r'^signup/$', views.signup, name='signup'),
    # # login
    url(r'^login/$', auth_views.login, {'template_name': 'core_app/login.html'},  name='login'),
    # # logout
    url(r'^logout/$', auth_views.logout, {'template_name': 'core_app/logout.html'}, name='logout'),
    # contact form
    url(r'^contact/$', views.contact, name='contact'),




    # # # password_reset
    # url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    # # # password_change
    # url(r'^password_change/$', auth_views.password_change, name='password_change'),
    # # # password_change
    # url(r'^password_change/done/$', auth_views.password_change_done, name='password_change_done'),
    # # # password_change
    # url(r'^password_reset/done/$', auth_views.password_reset, name='password_reset_done'),
    # # # password_change
    # url(r'^reset/<uidb64>/<token>$', auth_views.password_reset, name='password_reset_comfirm'),
]

handler404 = 'core_app.views.handler404'
handler500 = 'core_app.views.handler500'

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]