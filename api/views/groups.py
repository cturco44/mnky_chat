from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from user.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.models import Chat, DirectChat, DirectMessageLike, MemberOf, Message, DirectMessage, MessageLike
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.db.models import Q

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def active_chats(request):
    try:
        current_location = Point(float(request.data['long']), float(request.data['lat']), srid=4326)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    active_chats = Chat.objects.filter(polygon__covers=current_location)
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
            "lat": chat.location[1],
            "long": chat.location[0],
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
        radius_km = float(request.data['radius'])
        point = Point(float(request.data['long']), float(request.data['lat']), srid=4326)
        point.transform(6437)
        poly = point.buffer(radius_km*1000)
        poly.transform(4326)

        new_chat = Chat.objects.create(
            name=request.data["name"],
            description=request.data["description"],
            owner=request.user,
            location=Point(float(request.data['long']), float(request.data['lat'])),
            radius=float(request.data["radius"]),
            image=request.data["image"],
            polygon=poly,
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
        current_location = Point(float(request.data['long']), float(request.data['lat']), srid=4326)
        chat = Chat.objects.get(chat_id=request.data['chat_id'], polygon__covers=current_location)
        type = "Chat"
    except:
        pass
    try:
        chat = DirectChat.objects.get(chat_id=request.data['chat_id'])
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
                query = Message.objects.filter(chat=chat, timestamp__lt=cutoff.timestamp).order_by('-timestamp')
            except:
                return Response({"Error": "Invalid message id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            query = Message.objects.filter(chat=chat).order_by('-timestamp')[:20]
    
    message_list = []
    for message in query:
        likes = []
        if type == "Chat":
            likes = MessageLike.objects.filter(message=message)
        else:
            likes = DirectMessageLike.objects.filter(message=message)
        for like in likes:
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
            "likes": likes
        }
        message_list.append(x)
    return Response({"messages": message_list}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_files(request):
    try:
        current_location = Point(float(request.data['long']), float(request.data['lat']), srid=4326)
        chat = Chat.objects.get(chat_id=request.data['chat_id'], polygon__covers=current_location)
        type = "Chat"
    except:
        pass
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
        query = Message.objects.filter(chat=chat, file__isnull=False)
    else:
        if chat.user1 != request.user and chat.user2 != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        query = DirectMessage.objects.filter(chat=chat, file__isnull=False)
    
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
        current_location = Point(float(request.data['long']), float(request.data['lat']), srid=4326)
    except:
        return Response({"error": "invalid location"}, status=status.HTTP_400_BAD_REQUEST)
    
    query = MemberOf.objects.filter(user=request.user).filter(~Q(chat__polygon__covers=current_location))

    chat_log = []
    for item in query:
        most_recent_message = Message.objects.filter(chat=item.chat).latest('timestamp')
        chat_log.append({
            "name": item.chat.name,
            "image": item.chat.image.url,
            "timestamp": most_recent_message.timestamp
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
        user = User.objects.filter(username=request.data["username"])
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
            








    

