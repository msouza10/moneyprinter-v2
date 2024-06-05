from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fetch-news/', views.fetch_news, name='fetch_news'),
    path('list-news/', views.list_news, name='list_news'),
    path('process-news/', views.process_news, name='process_news'),
    path('settings/', views.settings, name='settings'),
]