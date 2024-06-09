from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('admin/', views.admin_view, name='admin'),
    path('register/', views.register_view, name='register'),  # Adiciona a URL de registro
    path('fetch-news/', views.fetch_news, name='fetch_news'),
    path('list-news/', views.list_news, name='list_news'),
    path('process-news/', views.process_news, name='process_news'),
    path('settings/', views.settings, name='settings'),
]