from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_view, name='game_view'),
    path('process_command/', views.process_command, name='process_command'),
    path('new_game/', views.new_game, name='new_game'),
]
