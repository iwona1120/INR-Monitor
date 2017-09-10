from django.conf.urls import url, include
from . import views
from django.contrib import admin
from django.views.generic import ListView, DetailView
from django.contrib.auth import views as auth_views


urlpatterns=[
	url(r'^$', views.home, name = "home"),
	url(r'^login/$', views.login, name = "log"),
	url(r'^logout/$', views.logout, name='logout'),
    url(r'^admin/', admin.site.urls),
	url(r'^home/$', views.home, name = 'home'),
	url(r'^home/add_INR', views.add_INR, name = "add_INR"),
	url(r'^home/next_visit', views.next_visit, name = "next_visit"),
	url(r'^home/all_visits/$', views.all_visits, name = "all_visit"),
	url(r'^home/all_visits/(?P<pk>\d+)$', views.detail, name = "datail"),
	url(r'^home/basicinfo', views.basicinfo, name = "basicinfo"),
	url(r'^home/missed_dose/$', views.missed_dose, name = "missed_dose"),
	url(r'^home/detail_prediction/$', views.detail_prediction, name = "detail_prediction"),
	url(r'^home/all_taken_drugs/$', views.all_taken_drugs, name = "all_taken_drugs"),
	url(r'^home/add_new_medicine/$', views.add_new_medicine, name = "add_new_medicine"),
	url(r'^home/statistic/$', views.statistic, name = "add_new_medicine"),
	url(r'^home/add_medicine/$', views.add_medicine, name = "add_medicine"),
	url(r'^home/all_other_medicine/$', views.all_other_medicine, name = "add_other_medicine"),
	url(r'^home/all_other_medicine/(?P<pk>\d+)$', views.details_other, name = "details_other"),
	url(r'^register/$', views.register, name= 'register'),
	url(r'^home/calendar/$', views.calendar, name= 'calendar'),
	]
