from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),
    path('feed/', views.post_feed, name='post-feed'),
    path('about/', views.about, name='about'),
    path('interactive/', views.interactive, name='interactive'),
]
