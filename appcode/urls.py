from django.urls import path
from .views import user_info, set_environment, delete_environment, get_apps, create_github_account, create_slack_account
from .chatbot import chat_bot

urlpatterns = [
    path('user_info/', user_info, name='user_info'),
    path('set_environment/', set_environment, name='set_environment'),
    path('delete_environment/', delete_environment, name='delete_environment'),
    path('get_apps/', get_apps, name='get_apps'),
    path('create_github_account/', create_github_account, name='create_github_account'),
    path('create_slack_account/', create_slack_account, name='create_slack_account'),
    path('chat_bot/', chat_bot, name='chatbot'),
]