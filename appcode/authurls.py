from . import auth
from django.urls import path

urlpatterns = [
    path('signup/', auth.signup, name="signup"),
    path('login/', auth.login, name="login"),
    path('changepass/', auth.changePassword, name="changepass")
]