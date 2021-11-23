from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from user.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.models import Chat, DirectChat, MemberOf, Message, DirectMessage
from django.contrib.gis.geos import Point
from itertools import chain
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def active_chats(request):
    try:
        current_location = Point(float(request.data['long']), float(request.data['lat']), srid=4326)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    active_chats = Chat.objects.filter(polygon__covers=current_location)
    if request.user.is_authenticated:
        active_dm1 = DirectChat.objects.filter(user1=request.user)
        active_dm2 = DirectChat.objects.filter(user2=request.user)
    else:
        active_dm1 = []
        active_dm2 = []
    
    return_data = {}
    return_data["active_chats"] = []
    for chat in active_chats:
        try:
            if chat.password:
                recent_message_content = None
                recent_message_timestamp = None
            else:
                recent_message = Message.objects.latest('timestamp')
                recent_message_content = recent_message.content
                recent_message_timestamp = recent_message.timestamp
        except:
            recent_message_content = None
            recent_message_timestamp = None
        
        x = {
            "chat_id": chat.chat_id,
            "description": chat.description,
            "recent_message_content": recent_message_content,
            "recent_message_timestamp": recent_message_timestamp
        }
        return_data["active_chats"].append(x)
    
    for chat in list(chain(active_dm1, active_dm2)):
        try:
            recent_message = DirectMessage.objects.latest('timestamp')
            recent_message_content = recent_message.content
            recent_message_timestamp = recent_message.timestamp
        except:
            recent_message_content = None
            recent_message_timestamp = None
        
        x = {
            "chat_id": chat.chat_id,
            "description": chat.description,
            "recent_message_content": recent_message_content,
            "recent_message_timestamp": recent_message_timestamp
        }
        return_data["active_chats"].append(x)
    
    return_data["active_chats"] = sorted(return_data["active_chats"], lambda x: x.recent_message_timestamp)

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
    user_query = MemberOf.objects.filter(chat=chat)
    user_list = []
    for member in user_query:
        if member == chat.owner:
            admin = True
        else:
            admin = False
        x = {
            "username": member.username,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "profile_pic": member.profile_pic.url,
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
    check_fields = ['name', 'description', 'lat', 'long', 'radius', 'image', 'radius']
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