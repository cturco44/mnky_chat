from django.contrib import admin
from .models import Chat

class ChatAdmin(admin.ModelAdmin):
    #readonly_fields = ('order_id', 'price', 'listing', 'bid', 'buyer', 'date', 'buyer_reminder', 'seller_reminder')
    list_display = ['chat_id', 'name', 'owner', 'location', 'radius']
    #list_filter = ['listing__event', 'listing__delivered', 'listing__buyer_confirmed']
    search_fields = ['name']

admin.site.register(Chat, ChatAdmin)