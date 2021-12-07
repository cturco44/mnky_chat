from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from user.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.models import Chat, DirectChat, DirectMessageLike, MemberOf, Message, DirectMessage, MessageLike
from django.shortcuts import get_object_or_404
from django.db.models import Q
from api.helpers.distance import get_chats
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def active_chats(request):
    try:
        lat = float(request.query_params['lat'])
        long = float(request.query_params['long'])
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    active_chats = get_chats(lat, long)
    if request.user.is_authenticated:
        chat_query = DirectChat.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        active_direct_chats = []
        for chat in chat_query:
            if DirectMessage.objects.filter(chat=chat).count() != 0:
                active_direct_chats.append(chat)
    else:
        active_direct_chats = []
    
    return_data = {}
    return_data["active_chats"] = []
    for chat in active_chats:
        try:
            if request.user.is_authenticated:
                MemberOf.objects.get(chat=chat, user=request.user)
                has_password_view_permission = True
        except:
            has_password_view_permission = False
        try:
            if chat.password and not has_password_view_permission:
                recent_message_content = None
                recent_message_timestamp = None
                password = True

            else:
                password = False
                recent_message = Message.objects.filter(chat=chat, timestamp__isnull=False).latest('timestamp')
                if recent_message.file:
                    recent_message = "FILE"
                else:
                    recent_message_content = recent_message.content
                recent_message_timestamp = recent_message.timestamp
        except:
            recent_message_content = None
            recent_message_timestamp = None
        

        x = {
            "chat_id": chat.chat_id,
            "name": chat.name,
            "description": chat.description,
            "lat": chat.lat,
            "long": chat.long,
            "radius": chat.radius,
            "image": chat.image.url,
            "recent_message_content": recent_message_content,
            "recent_message_timestamp": recent_message_timestamp,
            "require_password": password
        }
        return_data["active_chats"].append(x)
    
    for chat in active_direct_chats:
        try:
            recent_message = DirectMessage.objects.filter(chat=chat).latest('timestamp')
            recent_message_content = recent_message.content
            recent_message_timestamp = recent_message.timestamp
        except:
            recent_message_content = None
            recent_message_timestamp = None
        if chat.user1 == request.user:
            other_user = chat.user2
        else:
            other_user = chat.user1
        x = {
            "chat_id": chat.chat_id,
            "first_name": other_user.first_name,
            "last_name": other_user.last_name,
            "username": other_user.username,
            "profile_pic": other_user.profile_pic.url,
            "recent_message_content": recent_message_content,
            "recent_message_timestamp": recent_message_timestamp
        }
        return_data["active_chats"].append(x)
    
    return_data["active_chats"] = sorted(return_data["active_chats"], key=lambda x: (x['recent_message_timestamp'] is None, x['recent_message_timestamp']), reverse=True)

    return Response(return_data, status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chat_info(request):
    try:
        chat_id = request.data['chat_id']
    except:
        Response(status=status.HTTP_400_BAD_REQUEST)
    
    chat = get_object_or_404(Chat, chat_id=chat_id)
    try:
        MemberOf.objects.get(chat=chat, user=request.user)
    except:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    user_query = MemberOf.objects.filter(chat=chat)
    user_list = []
    for member in user_query:
        if member.user == chat.owner:
            admin = True
        else:
            admin = False
        x = {
            "username": member.user.username,
            "first_name": member.user.first_name,
            "last_name": member.user.last_name,
            "profile_pic": member.user.profile_pic.url,
            "admin": admin
        }
        user_list.append(x)

    return_dict = {
        "chat_id": chat.chat_id,
        "name": chat.name,
        "description": chat.description,
        "users": user_list,
    }
    return Response(return_dict, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_chat(request):
    check_fields = ['name', 'description', 'lat', 'long', 'radius', 'image']
    for required in check_fields:
        if required not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Convert to poly object
        radius = float(request.data['radius'])
        lat = float(request.data['lat'])
        long = float(request.data['long'])

        new_chat = Chat.objects.create(
            name=request.data["name"],
            description=request.data["description"],
            owner=request.user,
            lat=lat,
            long=long,
            radius=radius,
            image=request.data["image"],
        )
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if "password" in request.data:
        new_chat.password = request.data["password"]
        new_chat.save()
    
    MemberOf.objects.create(chat=new_chat, user=request.user)
    
    return_dict = {
        "chat_id": new_chat.chat_id,
        "name": new_chat.name,
        "image": new_chat.image.url,
    }
    return Response(return_dict, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_messages(request):
    try:
        lat = float(request.query_params['lat'])
        long = float(request.query_params['long'])
        x = Chat.objects.filter(chat_id=request.query_params['chat_id'])
        if len(x) != 1:
            raise Exception
        if not get_chats(lat, long, x):
            raise Exception
        
        chat = x[0]
        type = "Chat"
    except:
        try:
            chat = DirectChat.objects.get(chat_id=request.query_params['chat_id'])
            type = "DirectChat"
        except:
            return Response({"error": "invalid chat id"}, status=status.HTTP_400_BAD_REQUEST)
    
    if type == "Chat":
        try:
            MemberOf.objects.get(chat=chat, user=request.user)
        except:
            if chat.password:
                if not request.data['password']:
                    return Response({"error": "no password"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if request.data['password'] != chat.password:
                        return Response({"Error": "invalid, password"}, status=status.HTTP_403_FORBIDDEN)
            MemberOf.objects.create(chat=chat, user=request.user)
        if 'message_id' in request.data:
            try:
                cutoff = Message.objects.get(message_id=request.data['message_id'])[:20]
                query = Message.objects.filter(chat=chat, timestamp__lt=cutoff.timestamp).order_by('-timestamp')
            except:
                return Response({"Error": "Invalid message id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            query = Message.objects.filter(chat=chat).order_by('-timestamp')[:20]
    
    else:
        if chat.user1 != request.user and chat.user2 != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if 'message_id' in request.data:
            try:
                cutoff = DirectMessage.objects.get(message_id=request.data['message_id'])[:20]
                query = DirectMessage.objects.filter(chat=chat, timestamp__lt=cutoff.timestamp).order_by('-timestamp')
            except:
                return Response({"Error": "Invalid message id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            query = DirectMessage.objects.filter(chat=chat).order_by('-timestamp')[:20]
    
    message_list = []
    for message in query:
        likes = []
        if type == "Chat":
            db_likes = MessageLike.objects.filter(message=message)
        else:
            db_likes = DirectMessageLike.objects.filter(message=message)
        for like in db_likes:
            likes.append({
                "first_name": like.user.first_name,
                "last_name": like.user.last_name,
                "username": like.user.username,
                "profile_pic": like.user.profile_pic.url
            })
        if message.file:
            message_type = "file"
            content = message.file.url
        else:
            message_type = "message"
            content = message.content
        x = {
            "type": message_type,
            "message_id": message.message_id,
            "first_name": message.sender.first_name,
            "last_name": message.sender.last_name,
            "username": message.sender.username,
            "profile_pic": message.sender.profile_pic.url,
            "content": content,
            "timestamp": str(message.timestamp),
            "likes": likes
        }
        message_list.append(x)
    return Response({"messages": message_list}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_files(request):
    try:
        lat = float(request.data['lat'])
        long = float(request.data['long'])

        chat = Chat.objects.get(chat_id=request.data['chat_id'])
        if not get_chats(lat, long, chat):
            raise Exception
        type = "Chat"
    except:
        try:
            chat = DirectChat.objects.get(chat_id=request.data['chat_id'])
            type = "DirectChat"
        except:
            return Response({"error": "invalid chat id"}, status=status.HTTP_400_BAD_REQUEST)
    
    if type == "Chat":
        try:
            MemberOf.objects.get(chat=chat, user=request.user)
        except:
             return Response(status=status.HTTP_403_FORBIDDEN)
        query = Message.objects.filter(chat=chat).filter(~Q(file__in=['',None]))
    else:
        if chat.user1 != request.user and chat.user2 != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        query = DirectMessage.objects.filter(chat=chat).filter(~Q(file__in=['',None]))
    
    file_list = []
    for message in query:
        file_list.append({
            "file": message.file.url
        })
    
    return Response({"files": file_list}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chat_log(request):
    try:
        lat = float(request.query_params['lat'])
        long = float(request.query_params['long'])
    except:
        return Response({"error": "invalid location"}, status=status.HTTP_400_BAD_REQUEST)
    
    active_chats = [i.pk for i in get_chats(lat, long)]
    query = MemberOf.objects.filter(user=request.user).exclude(chat__pk__in=active_chats)

    chat_log = []
    for item in query:
        try:
            timestamp = Message.objects.filter(chat=item.chat).latest('timestamp').timestamp
        except:
            timestamp = None
        chat_log.append({
            "name": item.chat.name,
            "image": item.chat.image.url,
            "timestamp": timestamp
        })
    
    chat_log = sorted(chat_log, key=lambda x: (x['timestamp'] is None, x['timestamp']), reverse=True)

    for item in chat_log:
        item["timestamp"] = str(item["timestamp"])
    
    return Response({"chat_log": chat_log}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def direct_message(request):
    try:
        user = User.objects.get(username=request.data["username"])
    except:
        return Response({"error": "invalid username"}, status=status.HTTP_400_BAD_REQUEST)
    
    direct_chat = DirectChat.objects.create(user1=request.user, user2=user)

    return Response({"chat_id": direct_chat.chat_id}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def leave_chat(request):
    try:
        chat = Chat.objects.get(chat_id=request.data['chat_id'])
    except:
        return Response({"error": "could not find chat"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        x = MemberOf.objects.get(user=request.user, chat=chat)
        x.delete()
    except:
        return Response({"error": "user is not a member of this chat"}, status=status.HTTP_400_BAD_REQUEST)
    
    if chat.owner == request.user:
        other_users = MemberOf.objects.filter(chat=chat).filter(~Q(user=request.user))
        if not other_users:
            chat.delete()
        else:
            chat.owner = other_users[0]
            chat.save()
    return Response({}, status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_file(request):
    try:
        lat = float(request.data['lat'])
        long = float(request.data['long'])
        chat = Chat.objects.filter(chat_id=request.data['chat_id'])
        if len(chat) != 1:
            raise Exception
        if not get_chats(lat, long, chat):
            raise Exception
        chat = chat[0]
        type = "Chat"
    except:
        try:
            chat = DirectChat.objects.get(chat_id=request.data['chat_id'])
            type = "DirectChat"
        except:
            return Response({"error": "invalid chat id"}, status=status.HTTP_400_BAD_REQUEST)
    
    if type == "Chat":
        try:
            MemberOf.objects.get(chat=chat, user=request.user)
        except:
             return Response(status=status.HTTP_403_FORBIDDEN)
        msg = Message.objects.create(chat=chat, sender=request.user, file=request.data['file'])
    else:
        if chat.user1 != request.user and chat.user2 != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        msg = DirectMessage.objects.create(chat=chat, sender=request.user, file=request.data['file'])
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(msg.chat.chat_id,
        {
            'type': 'file_message',
            'chat_id': chat.chat_id,
            'message_id': msg.message_id,
            'first_name': msg.sender.first_name,
            'last_name': msg.sender.last_name,
            'username': msg.sender.username,
            'profile_pic': msg.sender.profile_pic.url,
            'content': msg.file.url,
            'timestamp': str(msg.timestamp)
        }
    )

    return Response({"message_id": msg.message_id}, status=200)
            
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_info(request):
    x = {
        "username": request.user.username,
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
    }
    return Response(x, status=200)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chat_pic(request):
    user = request.user
    if "chat_id" not in request.data or "img" not in request.data:
        return Response({"error": "pass a chat_id and profile pic"}, status=400)
    chat = get_object_or_404(Chat, chat_id=request.data["chat_id"])
    if chat.owner != user:
        return Response(status=status.HTTP_403_FORBIDDEN)
    chat.image = request.data["img"]
    chat.save()
    return Response(status=200)



    

