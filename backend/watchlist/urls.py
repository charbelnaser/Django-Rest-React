from django.urls import path
from . import views

urlpatterns = [
    # Watchlist management
    path('', views.get_watchlist, name='watchlist'),
    path('add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('remove/<str:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('check/<str:movie_id>/', views.check_watchlist_status, name='check_watchlist'),
    path('mark-watched/<str:movie_id>/', views.toggle_watch_status, name='mark_as_watched'),
]

