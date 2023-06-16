from rest_framework import serializers

from post.models import Post, PostLike, PostComment, CommentLike
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)


    class Meta:
        model = User
        fields = ['id', 'username', 'photo']

class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author=UserSerializer(read_only=True)
    post_likes_count=serializers.SerializerMethodField('get_post_likes_count')
    post_comment_count=serializers.SerializerMethodField('get_post_comment_count')
    me_liked=serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = Post
        fields = ['id', 'author', 'image', 'caption', 'created', 'post_likes_count', 'post_comment_count','me_liked']

    @staticmethod
    def get_post_likes_count(self,obj):
        return obj.likes.count()

    @staticmethod
    def get_post_comment_count(self,obj):
        return obj.comments.count()

    @staticmethod
    def get_me_liked(self,obj):
        request=self.context.get('request',None)
        if request and request.user.is_authenticated:
            if PostLike.objects.get(post=obj,author=request.user).exists():
                return True
            else:
                return False
        return False


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    replies=serializers.SerializerMethodField('get_replies')
    likes_count = serializers.SerializerMethodField('get_likes_count')
    me_liked=serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = PostComment
        fields = ['id', 'author', 'comment', 'created', 'replies', 'likes_count', 'me_liked']

    @staticmethod
    def get_replies(self,obj):
        if obj.child.exists():
            serializers=self.__class__(obj.child.all(),many=True,context=self.context)
            return serializers.data
        return None

    @staticmethod
    def get_me_liked(self,obj):
        user=self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(author=user).exists()
        return False

    @staticmethod
    def get_likes_count(self,obj):
        return obj.likes.count()



class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author=UserSerializer(read_only=True)

    class Meta:
        model=CommentLike
        fields=['id', 'author', 'post']




class CommentLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author=UserSerializer(read_only=True)

    class Meta:
        model=CommentLike
        fields=['id', 'author', 'comment']


