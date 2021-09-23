from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .forms.user_form import CustomUserChangeForm, CustomUserCreationForm
from .models.user_model import User


class CustomUserAdmin(BaseUserAdmin):
    """Customised UserAdmin class"""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ("email", "name", "surname", "date_joined", "last_login", "is_staff",
                    "is_superuser", "is_active")
    list_filter = ("email", "name", "surname", "is_staff", "is_superuser", "is_active")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                )
            },
        ),
    )
    # If you are using a custom ModelAdmin which is a subclass of django.contrib.auth.admin.
    # UserAdmin, then you need to add your custom fields to fieldsets (for fields to be used in
    # editing users) and to add_fieldsets (for fields to be used when creating a user)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
