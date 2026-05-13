from django.urls import path
from . import views

app_name = 'likes'

urlpatterns = [
    path('post/<slug:slug>/like/', views.toggle_like, name='toggle'),
]
