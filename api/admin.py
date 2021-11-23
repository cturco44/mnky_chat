from django.contrib import admin
from .models import Chat

class ChatAdmin(admin.ModelAdmin):
    readonly_fields = ('chat_id',)
    list_display = ['chat_id', 'name', 'owner']
    #list_filter = ['listing__event', 'listing__delivered', 'listing__buyer_confirmed']
    search_fields = ['name']

admin.site.register(Chat, ChatAdmin)