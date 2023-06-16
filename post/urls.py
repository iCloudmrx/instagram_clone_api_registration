from django.urls import path
from .views import post_list, post

urlpatterns = [
    path('posts/', post_list),
    path('post/<str:pk>/', post)
]
