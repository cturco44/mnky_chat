import geopy.distance
from api.models import Chat

def get_chats(lat, long, initial_query=Chat.objects.all()):
    in_range = []
    for chat in initial_query:
        chat_coord = (chat.lat, chat.long)
        person_coord = (lat, long)

        if geopy.distance.geodesic(chat_coord, person_coord).miles < chat.radius:
            in_range.append(chat)
    
    return in_range
