from django.contrib import admin
from apps.core.models import (
    User,
    CompanyInfo,
    UserActivation,
    ForgetPassword,
)


@admin.register(ForgetPassword)
class ForgetPasswordAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'organization', 'role', 'is_super_admin', 'is_staff', 'is_active')
    list_display_links = ('id', 'email', 'username')
    search_fields = ('email', 'username')
    list_filter = ('organization', 'role', 'is_super_admin', 'is_staff', 'is_active')
    list_per_page = 25

    fieldsets = (
        ('Basic Information', {
            'fields': ('email', 'username', 'password')
        }),
        ('Organization & Role', {
            'fields': ('organization', 'role', 'is_super_admin')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_admin', 'is_superuser', 'user_type')
        }),
    )


@admin.register(UserActivation)
class UserActivationAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    pass
