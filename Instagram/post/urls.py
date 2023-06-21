from django.urls import path
from .views import post_list, post, PostRetrieveUpdateDestoryAPI, post_create, PostCreateAPI,\
    PostCommentLikesListAPI, PostCommentCreateAPI,PostLikeListAPI,PostUpdateAPI, post_comment,\
    PostCommentListAPI,PostLikeAPI, PostCommentLikeAPI

urlpatterns = [
    path('', post_list),
    path('<uuid:pk>/', post),
    path('<uuid:pk>/likes', PostLikeListAPI.as_view()),
    path('<uuid:pk>/create-delete-like/', PostLikeAPI.as_view()),
    path('<uuid:pk>/comment/create/', PostCommentCreateAPI.as_view()),
    path('<uuid:pk>/comments/', PostCommentListAPI.as_view()),
    path('<uuid:pk>/comment/likes/', PostCommentLikesListAPI.as_view()),
    path('comment/<uuid:pk>/', post_comment),
    path('comment/<uuid:pk>/create-delete-like/', PostCommentLikeAPI.as_view()),
    path('create/', PostCreateAPI.as_view()),
    path('delete/<uuid:pk>/', PostRetrieveUpdateDestoryAPI.as_view()),
    path('update/<uuid:pk>/', PostUpdateAPI.as_view()),
]
