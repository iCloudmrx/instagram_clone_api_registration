from rest_framework import status
from rest_framework.response import Response

from .models import Post, PostLike, PostComment, CommentLike
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,AllowAny
from rest_framework.generics import ListAPIView,CreateAPIView,RetrieveUpdateDestroyAPIView
from shared.custom_pagination import CustomePagination
# Create your views here.

class PostsListAPI(ListAPIView):
    permission_classes([AllowAny,])
    serializer_class = PostSerializer
    pagination_class = CustomePagination
    http_method_names = ['get']

    def get_queryset(self):
        return Post.objects.all()

class PostCreateAPI(CreateAPIView):
    permission_classes([IsAuthenticated,])
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDestoryAPI(RetrieveUpdateDestroyAPIView):
    queryset = Post
    permission_classes([IsAuthenticatedOrReadOnly])
    serializer_class = PostSerializer

    def put(self, request, *args, **kwargs):
        post=self.get_object()
        serializer=self.serializer_class(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        post=self.get_object()
        post.delete()
        return Response({
            'success': True,
            'code': status.HTTP_204_NO_CONTENT,
            'message': "Post successfully deleted"
        })



class PostCommentListAPI(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes([AllowAny,])

    def get_queryset(self):
        post_id=self.kwargs['pk']
        queryset=Post.objects.filter(post__id=post_id)
        return queryset

class PostLikeListAPI(ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = ([IsAuthenticatedOrReadOnly, ])

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostLike.objects.filter(post__id=post_id)
        return queryset

class PostCommentCreateAPI(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = ([IsAuthenticated])

    def perform_create(self, serializer):
        post_id=self.kwargs['pk']
        serializer.save(author=self.request.user, post_id=post_id)

class PostCommentLikesAPI(ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = ([IsAuthenticatedOrReadOnly, ])

    def get_queryset(self):
        post_id=self.kwargs['pk']
        return CommentLike.objects.filter(post_id=post_id)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_create(request):
    serializer=PostSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(author=request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list(request):
    posts=Post.objects.all()
    serializers=PostSerializer(posts,many=True)
    return Response(serializers.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post(request, pk):
    post=Post.objects.get(id=pk)
    serializers=PostSerializer(post,many=False)
    return Response(serializers.data)



@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_like_list(request):
    post_likes=PostLike.objects.all()
    serializers=PostSerializer(post_likes,many=True)
    return Response(serializers.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_comment_list(request, pk):
    post_comments=PostComment.objects.filter(post=pk)
    serializers=PostSerializer(post_comments,many=True)
    return Response(serializers.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_comment_list(request, user_pk, post_pk):
    post_comment_likes=PostComment.objects.get(author=user_pk,post=post_pk)
    serializers=PostSerializer(post_comment_likes)
    return Response(serializers.data)
