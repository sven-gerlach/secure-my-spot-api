from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms.user_form import CustomerUserChangeForm, CustomUserCreationForm
from .models.user_model import User


class CustomUserAdmin(UserAdmin):
    """Customised UserAdmin class"""

    add_form = CustomUserCreationForm
    form = CustomerUserChangeForm
    model = User
    list_display = ("email", "name", "surname", "is_staff", "is_superuser", "is_active")
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
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
