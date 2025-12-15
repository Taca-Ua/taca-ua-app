"""
Django admin configuration for admin_api app
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""

    list_display = ("id", "username", "email", "full_name", "role", "course_id", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email", "full_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("full_name", "email")}),
        ("Permissions", {"fields": ("role", "course_id", "course_abbreviation", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role", "course_id", "course_abbreviation", "full_name"),
            },
        ),
    )
