from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    #readonly_fields = ('order_id', 'price', 'listing', 'bid', 'buyer', 'date', 'buyer_reminder', 'seller_reminder')
    list_display = ['username', 'email', 'first_name', 'last_name']
    #list_filter = ['listing__event', 'listing__delivered', 'listing__buyer_confirmed']
    search_fields = ['email', 'username']

admin.site.register(User, UserAdmin)