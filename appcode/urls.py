from django.urls import path
from .views import user_info, set_environment, delete_environment, get_apps, create_github_account, create_slack_account, create_app, create_role, get_role_apps, get_images, get_profile, set_single_app
from .chatbot import chat_bot

urlpatterns = [
    path('user_info/', user_info, name='user_info'),
    path('set_environment/', set_environment, name='set_environment'),
    path('delete_environment/', delete_environment, name='delete_environment'),
    path('get_apps/', get_apps, name='get_apps'),
    path('create_github_account/', create_github_account, name='create_github_account'),
    path('create_slack_account/', create_slack_account, name='create_slack_account'),
    path('chat_bot/', chat_bot, name='chatbot'),
    path('create_role/', create_role, name='create_role'),
    path('create_app/', create_app, name='create_app'),
    path('get_role_apps/', get_role_apps, name='get_role_apps'),
    path('get_images/<str:role_name>/', get_images, name='get_images'),
    path('get_profile/', get_profile, name='get_profile'),
    path('set_single_app/<str:app_name>', set_single_app, name='set_single_app'),
]