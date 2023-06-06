from django.contrib import admin
from . models import Auth, Userapp, App
# Register your models here.

class AuthAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'password']

admin.site.register(Auth, AuthAdmin)
admin.site.register(Userapp)
admin.site.register(App)