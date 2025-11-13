from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'full_name', 'role', 'is_staff', 'is_active', 'is_email_verified', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_email_verified', 'role', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'updated_at', 'last_login', 'last_activity')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role', 'bio', 'avatar')
        }),
        ('Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified')
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'updated_at', 'last_activity')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )


    def full_name(self, obj):
        """Display the full name in an admin list."""
        return obj.get_full_name()


    full_name.short_description = 'Full Name'
