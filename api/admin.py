from django.contrib import admin
from .models import Chat, MemberOf

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

admin.site.register(Chat, ChatAdmin)
admin.site.register(MemberOf, MemberOfAdmin)