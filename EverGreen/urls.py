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
    # file_upload
    url(r'^upload_transactions/$', views.upload_transactions, name='upload_transactions'),
    # display_transaction_details
    url(r'^display_transaction_details/$', views.display_transaction_details, name='display_transaction_details'),
    # display_tag_details
    url(r'^update_tags/$', views.update_tags, name='update_tags'),
    # display_rule_details
    url(r'^update_rules/$', views.update_rules, name='update_rules'),
    url(r'^delete_user_account/$', views.delete_user_account, name='delete_user_account'),
    url(r'^update_account/$', views.update_account, name='update_account'),
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
    url(r'^password_reset/$', auth_views.password_reset, {'template_name': 'core_app/password_reset.html'}, name='password_reset'),
    # # # password_change
    url(r'^password_change/$', auth_views.password_change, {'template_name': 'core_app/password_change.html'}, name='password_change'),
    # # # password_change
    url(r'^accounts/password_change/done/$', auth_views.password_change_done, {'template_name': 'core_app/change_done.html'}, name='password_change_done'),
    # # # password_change
    url(r'^accounts/password_reset/done/$', auth_views.password_reset, {'template_name': 'core_app/change_done.html'}, name='password_reset_done'),
    # # # # password_change
    # url(r'^reset/<uidb64>/<token>$', auth_views.password_reset, {'template_name': 'core_app/password_reset.html'}, name='password_reset_comfirm'),


    # api
    url(r'^new_chart_data/$', views.new_chart_data, name='new_chart_data'),
    url(r'^first_charts/$', views.first_chart, name='first_charts'),
    url(r'^get_months/$', views.get_months, name='get_months'),
    url(r'^new_tag_data/$', views.new_tag_data, name='new_tag_data'),
    url(r'^new_income_tag_data/$', views.new_income_tag_data, name='new_income_tag_data'),
    url(r'^update_cat_dropdown/$', views.update_cat_dropdown, name='update_cat_dropdown'),
    url(r'^transaction_details/$', views.transaction_details, name='transaction_details'),
    url(r'^drill_down/$', views.drill_down, name='drill_down'),
    url(r'^drill_down_chart_click/$', views.drill_down_chart_click, name='drill_down_chart_click'),

    # class views
    path('transaction-detail/<int:pk>/', views.TransactionUpdate.as_view(), name='transaction-update'),
    path('transaction-delete/<int:pk>/', views.TransactionDelete.as_view(), name='transaction-delete'),
    path('tag-detail/<int:pk>/', views.TagsUpdate.as_view(), name='tags-update'),
    path('tag-delete/<int:pk>/', views.TagsDelete.as_view(), name='tags-delete'),
    path('rule-detail/<int:pk>/', views.RuleUpdate.as_view(), name='rules-update'),
    path('rule-delete/<int:pk>/', views.RuleDelete.as_view(), name='rules-delete'),
    path('account-update/<int:pk>/', views.AccountUpdate.as_view(), name='account-update'),
    path('account-delete/<int:pk>/', views.AccountDelete.as_view(), name='account-delete'),

]

handler404 = 'core_app.views.handler404'
handler500 = 'core_app.views.handler500'

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]