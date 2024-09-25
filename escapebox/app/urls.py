from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_view, name='game_view'),
    path('process_command/', views.process_command, name='process_command'),
    path('new_game/', views.new_game, name='new_game'),
    path('new_session/', views.new_session, name='new_session'),
]
