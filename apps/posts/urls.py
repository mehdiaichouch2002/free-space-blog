from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.blog, name='blog'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('category/<slug:slug>/', views.category_posts, name='category'),
    path('post/new/', views.post_create, name='create'),
    path('post/<slug:slug>/', views.post_detail, name='detail'),
    path('post/<slug:slug>/edit/', views.post_edit, name='edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='delete'),
]
