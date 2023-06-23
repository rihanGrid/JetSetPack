from django.contrib import admin
from . models import Auth, Userapp, App, Role, AppName
# Register your models here.

class AuthAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'password']

admin.site.register(Auth, AuthAdmin)
admin.site.register(Userapp)
admin.site.register(App)
admin.site.register(Role)
admin.site.register(AppName)
