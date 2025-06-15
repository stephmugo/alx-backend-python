from django.contrib import admin
from .models import Message

# Register the Message model with the admin site
admin.site.register(Message)