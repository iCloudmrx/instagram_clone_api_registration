from django.urls import path
from . import views

urlpatterns=[
    path('list/', views.ChatRoomListAPI.as_view()),
    path('<uuid:pk>/create/', views.ChatRoomCreateAPI.as_view()),
    path('<uuid:pk>/update/', views.ChatRoomUpdateAPI.as_view()),
    path('<uuid:pk>/delete/', views.chat_message_delete),
]