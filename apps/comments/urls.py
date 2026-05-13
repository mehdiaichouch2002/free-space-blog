from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('post/<slug:slug>/comment/', views.add_comment, name='add'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete'),
]
