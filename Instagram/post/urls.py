from django.urls import path
from .views import post_list, post, PostRetrieveUpdateDestoryAPI, post_create, PostCreateAPI,\
    PostCommentLikesAPI, PostCommentCreateAPI,PostLikeListAPI

urlpatterns = [
    path('', post_list),
    path('<uuid:pk>/', post),
    path('<uuid:pk>/likes', PostLikeListAPI.as_view()),
    path('<uuid:pk>/comment/create/', PostCommentCreateAPI.as_view()),
    path('<uuid:pk>/comments/', PostCommentLikesAPI.as_view()),
    path('<uuid:pk>/comment/likes/', PostCommentLikesAPI.as_view()),
    path('create/', PostCreateAPI.as_view()),
    path('delete/<uuid:pk>/', PostRetrieveUpdateDestoryAPI.as_view())
]
