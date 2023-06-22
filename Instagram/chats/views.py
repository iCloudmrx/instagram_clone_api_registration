from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.models import User
from .models import ChatRoom
from .serializers import ChatRoomSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView

# Create your views here.
class ChatRoomListAPI(ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = ([IsAuthenticated,])

    def get_queryset(self):
        return ChatRoom.objects.filter(sender=self.request.user, is_active=True)

class ChatRoomCreateAPI(CreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = ([IsAuthenticated,])

    def perform_create(self, serializer):
        sender = self.request.user
        print(sender)
        receiver_id = self.kwargs['pk']
        serializer.save(sender=sender, receiver_id=receiver_id, is_active=True)
        


class ChatRoomUpdateAPI(UpdateAPIView):
    queryset = ChatRoom
    serializer_class = ChatRoomSerializer
    permission_classes = ([IsAuthenticated,])

    def put(self, request, *args, **kwargs):
        sender = request.user
        receiver = self.get_object()
        print("User",receiver)
        serializer = self.serializer_class(sender, receiver, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


    def patch(self, request, *args, **kwargs):
        sender = request.user
        receiver_id = self.kwargs['pk']
        serializer = self.serializer_class(sender, receiver_id, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class ChatRoomDeleteAPI(DestroyAPIView):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = ([IsAuthenticated,])

    def delete(self, request, *args, **kwargs):
        sender = request.user
        receiver = self.get_object()
        message = ChatRoom.objects.get(sender=sender, receiver=receiver)
        message.delete()
        return Response({
            'success': True,
            'code': status.HTTP_204_NO_CONTENT,
            'message': "Message successfully deleted"
        })

@api_view(['DELETE'])
def chat_message_delete(request, pk):
    sender = request.user
    receiver = User.objects.get(id=pk)
    if ChatRoom.objects.get(sender=sender, receiver=receiver).exists():
        message = ChatRoom.objects.get(sender=sender, receiver=receiver)
        message.delete()
        return Response({
            'success': True,
            'code': status.HTTP_204_NO_CONTENT,
            'message': "Message successfully deleted"
        })
    else:
        return Response({
            'success': True,
            'code': status.HTTP_404_NOT_FOUND,
            'message': "Message do not exist"
        })

