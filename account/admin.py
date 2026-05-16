from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'college', 'major', 'is_staff')

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('college', 'major')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('college', 'major')}),
    )