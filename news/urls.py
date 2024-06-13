from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('admin/', views.admin_view, name='admin'),
    path('register/', views.register_view, name='register'),
    path('fetch-news/', views.fetch_news, name='fetch_news'),
    path('list-news/', views.list_news, name='list_news'),
    path('process-news/', views.process_news, name='process_news'),
    path('settings/', views.settings, name='settings'),
    path('select-clips/', views.select_clips, name='select_clips'),
    path('fetch-clips/', views.fetch_clips, name='fetch_clips'),
    path('list-clips/', views.list_clips, name='list_clips'),
    path('download-clip/<str:clip_id>/', views.download_clip_view, name='download_clip'),
    path('list-game-ids/', views.list_game_ids, name='list_game_ids'),
    path('search-game-ids/', views.search_game_ids, name='search_game_ids'),
]