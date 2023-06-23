from django.db import models

# Create your models here.


class Auth(models.Model):
    username = models.CharField(max_length=256, null=False, unique=True, primary_key=True)
    email = models.CharField(max_length=256, null=False)
    password = models.CharField(max_length=256, null=False)


class App(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Userapp(models.Model):
    username = models.CharField(max_length=256, null=False, unique=True)
    app = models.ManyToManyField(App)

    def __str__(self):
        return self.username
    
    
class AppName(models.Model):
    name = models.CharField(max_length=50, null=False, unique=True)

    def __str__(self):
        return self.name
    
    
class Role(models.Model):
    name = models.CharField(max_length=25, null=False, unique=True)
    apps = models.ManyToManyField(AppName)

    def __str__(self):
        return self.name
    