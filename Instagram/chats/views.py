from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
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
        return ChatRoom.objects.filter(sender=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_message_list(request):
    try:
        messages = ChatRoom.objects.filter(sender=request.user)
    except ChatRoom.DoesNotExist:
        return Response({
            'success': False,
            'message': "Messages do not exist"
                        },
            status=status.HTTP_404_NOT_FOUND)
    return Response({
        'success': True,
        "message": "Messages are got",
        'data': messages
    },
        status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def chat_message_delete(request, pk):
    sender = request.user
    receiver = User.objects.get(id=pk)
    if ChatRoom.objects.filter(sender=sender, receiver=receiver).exists():
        message = ChatRoom.objects.filter(sender=sender, receiver=receiver)[0]
        message.delete()
        return Response({
            'success': True,
            'message': "Message successfully deleted"
        },
        status=status.HTTP_204_NO_CONTENT)

    else:
        return Response({
            'success': True,
            'message': "Message do not exist"
        },
        status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_message_create(request, pk):
    sender = request.user
    receiver = User.objects.get(id=pk)
    serializer = ChatRoomSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(sender=sender, receiver=receiver)
        return Response({
            'success': True,
            'message': "Message successfully create",
            'data': serializer.data
        },
        status=status.HTTP_201_CREATED)
    return Response({
        'success': True,
        'message': "Message is not created",
        'data': serializer.errors
    },
        status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def chat_message_update(request, pk):
    try:
        message = ChatRoom.objects.get(id=pk)
    except ChatRoom.DoesNotExist:
        return Response({
            'success': False,
            'message': "Message do not exist"
        },
        status=status.HTTP_404_NOT_FOUND)
    serializer=ChatRoomSerializer(message, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': "Message successfully update",
            'data': serializer.data
        },
        status=status.HTTP_204_NO_CONTENT)
    return Response({
        'success': True,
        'message': "Message is not created",
        'data': serializer.errors
    },
        status=status.HTTP_400_BAD_REQUEST)
