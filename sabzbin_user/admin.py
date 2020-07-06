from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from . import models
from .models import User, UserAddress


class UserAddressesInline(admin.TabularInline):
    model = UserAddress
    extra = 0


@admin.register(User)
class MyUserAdmin(UserAdmin):
    fieldsets = ((None, {'fields': ('phone_number',)}),
                 (_('Personal info'), {'fields': ('first_name', 'last_name', "avatar",)}),
                 (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                                'groups', 'user_permissions')}),
                 (_('Important dates'), {'fields': ('updated', 'last_login', 'created')}),)
    ordering = ('-created',)
    list_filter = ['created', 'is_superuser', 'is_staff', ]
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': ('phone_number',),
    }),)
    list_display = ('phone_number', 'first_name', 'last_name', 'created',)
    readonly_fields = ('created', 'last_login', 'updated')
    search_fields = ['phone_number', ]
    inlines = [UserAddressesInline]


class UserScoreBaseAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'type',
                    'point',)
    list_filter = ('user',
                   'type',)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    class Meta:
        abstract = True


@admin.register(models.UserScore)
class UserScoreAdmin(UserScoreBaseAdmin):

    def has_add_permission(self, request):
        return False


@admin.register(models.UserScoreTransaction)
class UserScoreTransactionAdmin(UserScoreBaseAdmin):
    def has_add_permission(self, request):
        return True


@admin.register(models.UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    pass
