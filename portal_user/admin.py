from django.contrib import admin

from .models import PortalUser

# Register your models here.


class PortalUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'email', "is_staff",
                    "is_active", "user_role")
    list_filter = ('is_active', 'is_staff', 'is_superuser', "user_role")
    search_fields = ('first_name', 'email', 'consumer_number', "user_role")


admin.site.register(PortalUser, PortalUserAdmin)
