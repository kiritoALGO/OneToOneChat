from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Message

User = get_user_model()


class PlainTextUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    fieldsets = list(UserAdmin.fieldsets)
    fieldsets[0] = (None, {'fields': ('username', 'password')})

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None and obj.pk:
            demo_passwords = {
                'alice': 'password123',
                'bob': 'password123',
                'admin': 'admin123',
            }
            plain_password = demo_passwords.get(obj.username, '')
            form.base_fields['password'] = forms.CharField(
                label='Password',
                required=False,
                initial=plain_password,
                help_text='Plain text password for demo purposes',
                widget=forms.TextInput(attrs={'readonly': 'readonly'}),
            )
        return form


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'created_at')
    list_filter = ('sender', 'receiver', 'created_at')
    search_fields = ('content', 'sender__username', 'receiver__username')
    ordering = ('-created_at',)


admin.site.unregister(User)
admin.site.register(User, PlainTextUserAdmin)
