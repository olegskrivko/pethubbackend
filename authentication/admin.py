from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
#from .forms import CustomUserCreationForm  # import your form

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    #add_form = CustomUserCreationForm

    list_display = [
        'email', 'username', 'is_active', 'is_staff', 'is_superuser'
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'username']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'avatar')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'username', 'avatar',
                'is_staff', 'is_superuser'
            )
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
