from django.urls import path
from . import views

urlpatterns=[
    path('list/', views.ChatRoomListAPI.as_view()),
    path('<uuid:pk>/create/', views.chat_message_create),
    path('<uuid:pk>/update/', views.chat_message_update),
    path('<uuid:pk>/delete/', views.chat_message_delete),
]