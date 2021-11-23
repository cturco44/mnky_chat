from django.contrib import admin
from .models import Chat, MemberOf, Message, DirectMessage, DirectChat, MessageLike, DirectMessageLike

class ChatAdmin(admin.ModelAdmin):
    readonly_fields = ('chat_id',)
    list_display = ['chat_id', 'name', 'owner']
    #list_filter = ['listing__event', 'listing__delivered', 'listing__buyer_confirmed']
    search_fields = ['name']

class MemberOfAdmin(admin.ModelAdmin):
    list_display = ['chat_name', 'username']
    #list_filter = ['listing__event', 'listing__delivered', 'listing__buyer_confirmed']
    search_fields = ['chat__name', 'user__username', 'user__email']
    def username(self, obj):
        return obj.user.username
    username.short_description = 'username'
    
    def chat_name(self, obj):
        return obj.chat.name
    chat_name.short_description = 'chat_name'

class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ('message_id',)
    list_display = ['message_id', 'chat', 'sender', 'content']

class DirectMessageAdmin(admin.ModelAdmin):
    readonly_fields = ('message_id',)
    list_display = ['message_id', 'sender', 'content']
class DirectChatAdmin(admin.ModelAdmin):
    readonly_fields = ('chat_id',)
    list_display = ['chat_id', 'user1', 'user2']

class DirectMessageLikeAdmin(admin.ModelAdmin):
    list_display = ['message', 'user']

class MessageLikeAdmin(admin.ModelAdmin):
    list_display = ['message', 'user']


admin.site.register(Chat, ChatAdmin)
admin.site.register(MemberOf, MemberOfAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(DirectMessage, DirectMessageAdmin)
admin.site.register(DirectChat, DirectChatAdmin)
admin.site.register(DirectMessageLike, DirectMessageLikeAdmin)
admin.site.register(MessageLike, MessageLikeAdmin)
