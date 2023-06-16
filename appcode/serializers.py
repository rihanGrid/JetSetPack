from rest_framework import serializers
from .models import App, Userapp

class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = '__all__'


class Userapp(serializers.ModelSerializer):
    class Meta:
        model = Userapp
        fields = '__all__'

        