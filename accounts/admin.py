from django.contrib import admin
from .models import MyUser,Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class MyUserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]
    list_display = ('username','phone_number','is_admin')
    search_fields = ('username','phone_number')

admin.site.register(MyUser, MyUserAdmin)