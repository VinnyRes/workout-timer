from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('log/', views.weights_log, name='weights_log'),
    path('save-workout/', views.save_workout, name='save_workout'),
    path('weights-log/', views.weights_log, name='weights_log'), 
    path('save-workout-log/', views.save_workout_log, name='save_workout_log'),
    path('summary/', views.summary, name="summary"),
]