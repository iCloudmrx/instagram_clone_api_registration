from django.contrib import admin
from .models import ChatRoom
# Register your models here.
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'message']
    search_fields = ['sender', 'receiver']