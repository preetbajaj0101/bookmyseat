from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    # You can add your customizations here later
    pass

# Unregister the original User admin
admin.site.unregister(User)
# Register the new User admin
admin.site.register(User, UserAdmin)