# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from api.helpers.socket_helpers import all_active_chat_ids, active_chat_changes, get_chat, get_message
from api.models import Message, DirectMessage, MessageLike, DirectMessageLike

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        if not self.scope['user'].is_authenticated:
            raise Exception
        header_dict = {}
        for item in self.scope['headers']:
            header_dict[item[0]] = item[1]
        if b'lat' not in header_dict or b'long' not in header_dict:
            raise Exception
        lat = float(header_dict[b'lat'].decode())
        long = float(header_dict[b'long'].decode())
        self.joined_chat_ids = all_active_chat_ids(self.scope['user'], lat, long)

        for chat_id in self.joined_chat_ids:
            async_to_sync(self.channel_layer.group_add)(
                chat_id,
                self.channel_name
            )

        self.accept()

    def disconnect(self, close_code):
        for chat_id in self.joined_chat_ids:
            async_to_sync(self.channel_layer.group_discard)(
                chat_id,
                self.channel_name
            )
    
    def update(self, data):
        if not self.scope['user'].is_authenticated:
            return
        header_dict = {}
        for item in self.scope['headers']:
            header_dict[item[0]] = item[1]
        if b'lat' not in header_dict or b'long' not in header_dict:
            return
        lat = float(data['lat'])
        long = float(data['long'])

        added_chats, removed_chats, new_chat_set = active_chat_changes(self.scope['user'], lat, long, self.joined_chat_ids)
        for item in added_chats:
            async_to_sync(self.channel_layer.group_add)(
                item,
                self.channel_name
            )
        for item in removed_chats:
            async_to_sync(self.channel_layer.group_discard)(
                item,
                self.channel_name
            )
        self.joined_chat_ids = new_chat_set

    # Receive message from WebSocket
    def receive(self, text_data):
        if not self.scope['user'].is_authenticated:
            return
        data = json.loads(text_data)
        self.update(data)

        

        if data['type'] == 'chat_message':
            type, chat = get_chat(data['chat_id'])
            if data['chat_id'] not in self.joined_chat_ids:
                return
            if type == "Chat":
                msg = Message.objects.create(
                    chat=chat, 
                    sender=self.scope['user'], 
                    content=data['content'])
            elif type == "DirectChat":
                msg = DirectMessage.objects.create(
                    chat=chat, 
                    sender=self.scope['user'], 
                    content=data['content'])
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                data['chat_id'],
                {
                    'type': 'chat_message',
                    'chat_id': chat.chat_id,
                    'message_id': msg.message_id,
                    'first_name': msg.sender.first_name,
                    'last_name': msg.sender.last_name,
                    'username': msg.sender.username,
                    'profile_pic': msg.sender.profile_pic.url,
                    'content': msg.content,
                    'timestamp': str(msg.timestamp)
                }
            )
        elif data['type'] == 'update':
            pass
        elif data['type'] == 'file_message':
            type, msg = get_message(data['message_id'])
            chat = msg.chat
            if chat.chat_id not in self.joined_chat_ids:
                return
            async_to_sync(self.channel_layer.group_send)(
                chat.chat_id,
                {
                    'type': 'file_message',
                    'chat_id': chat.chat_id,
                    'message_id': msg.message_id,
                    'first_name': msg.sender.first_name,
                    'last_name': msg.sender.last_name,
                    'username': msg.sender.username,
                    'profile_pic': msg.sender.profile_pic.url,
                    'content': msg.content,
                    'timestamp': str(msg.timestamp)
                }
            )
        elif data['type'] == 'like_message':
            type, msg = get_message(data['message_id'])
            if msg.chat.chat_id not in self.joined_chat_ids:
                return
            if type == "Message":
                like = MessageLike.objects.create(message=msg, user=self.scope['user'])
            elif type == "DirectMessage":
                like = DirectMessageLike.objects.create(message=msg, user=self.scope['user'])
            
            async_to_sync(self.channel_layer.group_send)(
                like.message.chat.chat_id,
                {
                    'type': 'like_message',
                    'chat_id': like.message.chat.chat_id,
                    'message_id': like.message.message_id,
                    'sender_first_name': like.user.first_name,
                    'sender_last_name': msg.sender.last_name,
                    'sender_username': like.user.username,
                    'sender_profile_pic': like.user.profile_pic.url,
                    'recipient_first_name': like.message.sender.first_name,
                    'recipient_last_name': like.message.sender.last_name,
                    'recipient_username': like.message.sender.username,
                    'recipient_profile_pic': like.message.sender.profile_pic.url,
                }
            )
    
    def chat_message(self, event):
        self.send(text_data=json.dumps(event))
    
    def file_message(self, event):
        self.send(text_data=json.dumps(event))

    def like_message(self, event):
        self.send(text_data=json.dumps(event))
