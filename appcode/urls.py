from django.urls import path
from .views import user_info, set_environment, delete_environment, get_apps

urlpatterns = [
    path('user_info/', user_info, name='user_info'),
    path('set_environment/', set_environment, name='set_environment'),
    path('delete_environment/', delete_environment, name='delete_environment'),
    path('get_apps/', get_apps, name='get_apps'),
]