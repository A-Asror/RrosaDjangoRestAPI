from django.contrib import admin

from .models import UserModel, JwtModel


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', )  # 'username',
    list_display_links = ('email', )
    list_filter = ('is_active', )
    search_fields = ('username', 'email', 'status')
    exclude = ('is_active', )


admin.site.register((JwtModel,))
