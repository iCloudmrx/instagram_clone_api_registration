from rest_framework.response import Response

from .models import Post, PostLike, PostComment, CommentLike
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
# Create your views here.

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
