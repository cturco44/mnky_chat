from api.models import MemberOf, DirectChat, Chat, Message, DirectMessage
from django.db.models import Q
from api.helpers.distance import get_chats

def all_active_chat_ids(user, lat, long):
    all_groups = [i.pk for i in get_chats(lat, long)]
    all_groups = MemberOf.objects.filter(user=user, chat__pk__in=all_groups)
    all_direct_chats = DirectChat.objects.filter(Q(user1=user) | Q(user2=user))

    return_list = set()
    for item in all_groups:
        return_list.add(item.chat.chat_id)
    for item in all_direct_chats:
        return_list.add(item.chat_id)
    
    return return_list

def active_chat_changes(user, lat, long, active_ids):
    """ Returns tuple of sets added chats, removed chats, new_chat_set """
    new_chat_set = all_active_chat_ids(user, lat, long)
    added_chats = set()
    removed_chats = set()

    for item in new_chat_set:
        if item not in active_ids:
            added_chats.add(item)
    
    for item in active_ids:
        if item not in new_chat_set:
            removed_chats.add(item)
    
    return (added_chats, removed_chats, new_chat_set)

def get_chat(chat_id):
    try:
        x = Chat.objects.get(chat_id=chat_id)
        return ("Chat", x)
    except:
        pass
    try:
        x = DirectChat.objects.get(chat_id=chat_id)
        return ("DirectChat", x)
    except:
        raise Exception

def get_message(message_id):
    try:
        x = Message.objects.get(message_id=message_id)
        return ("Message", x)
    except:
        pass
    try:
        x = DirectMessage.objects.get(message_id=message_id)
        return ("DirectMessage", x)
    except:
        raise Exception


