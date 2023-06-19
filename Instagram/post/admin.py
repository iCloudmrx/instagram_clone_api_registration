from django.contrib import admin
from .models import Post, PostLike, CommentLike, PostComment
# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'caption', 'created']
    search_fields = ['id', 'author__username', 'caption']

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'created']
    search_fields = ['id', 'author__username']


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'created']
    search_fields = ['id', 'author__username', 'comment']

@admin.register(CommentLike)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'comment', 'created']
    search_fields = ['id', 'author__username']
