from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
#from .forms import CustomUserCreationForm  # import your form

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    #add_form = CustomUserCreationForm

    list_display = [
        'email', 'username', 'is_active', 'is_staff', 'is_superuser',
        'is_subscribed', 'subscription_start', 'subscription_type'
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'is_subscribed']
    search_fields = ['email', 'username']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'avatar')}),
        ('Subscription', {
            'fields': (
                'is_subscribed', 'subscription_start', 'subscription_end',
                'subscription_type', 'stripe_customer_id'
            )
        }),
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
                'is_staff', 'is_superuser', 'is_subscribed'
            )
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
