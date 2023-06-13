from django.shortcuts import render
# from rest_framework.generics import get_object_or_404
from .models import App, Userapp
from django.http import JsonResponse
from .authentication import CustomIsAuthenticated, TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
# from django.core import serializers
# from rest_framework import generics, permissions
# from rest_framework.views import APIView
import ansible_runner
import re
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
# import json
import requests
from django.shortcuts import redirect




@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['ip_address', 'os'],
        properties={
            'ip_address': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s IP address'),
            'os': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s operating system (e.g., "mac")'),
        },
    ),
    responses={
        200: openapi.Response(
            description='Inventory file created successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                },
            ),
        ),
        400: openapi.Response(
            description='OS not defined',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
    }
)

@api_view(['POST'])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([TokenAuthentication])
def user_info(request):
    """
    Store user information.

    This endpoint allows authenticated users to store their information, including IP address and operating system.

    ---
    # Request Body
    - `ip_address` (string): User's IP address.
    - `os` (string): User's operating system (e.g., "mac").

    # Response
    - `message` (string): Success or error message.

    """
    if request.method == 'POST':
        username = request.user
        ip_address = request.data.get('ip_address')
        os = request.data.get('os')
        # print("user_name----->", username)
        # print("ip_address---->", ip_address)
        # print("operating system---->", os)
        if os == "mac":
            inventory_line = f"{username}@{ip_address}"

            with open('Ansible_create/inventory.ini', 'w') as inventory_file:
                inventory_file.write(f"[client]\n{inventory_line}\n")


            return JsonResponse({'message': 'Inventory file created successfully'})
        else:
            return JsonResponse({'message': 'OS not defined'})




@swagger_auto_schema(
    method='post',
    responses={
        200: openapi.Response(
            description='Installation Successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                },
            ),
        ),
        400: openapi.Response(
            description='Installation Failed',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
    }
)

@api_view(['POST'])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([TokenAuthentication])
def set_environment(request):
    """
    Set environment.

    This endpoint allows authenticated users to set the environment using Ansible.

    ---
    # Response
    - `message` (string): Success or error message.
    """
    inventory_path = '/Users/rsah/Desktop/JetSetPack/jetsetpack/Ansible_create/inventory.ini'
    playbook_path = '/Users/rsah/Desktop/JetSetPack/jetsetpack/Ansible_create/main.yml'
    # host = 'client'
    # host = request.data.get('host')
    # roles = request.data.get('roles')

    try:
        options = {
            'inventory': inventory_path,
            'playbook': playbook_path,
            # 'extravars': {'host': host, 'roles': roles}
        }

        r = ansible_runner.run(**options)
        for event in r.events:
            if event['event'] == 'runner_on_ok':
                result = event['event_data']

                t_name = result['task']
                task_status = result['res']['changed']
                if t_name == 'Gathering Facts':
                    pass
                else:
                    regex = re.compile(r"Install\s+(.*)")
                    matches = regex.findall(t_name)
                    task_name = matches[0]
                    if task_status:
                        print(f"Task '{task_name}' was successful")

                        user = Userapp.objects.filter(username=request.user).exists()
                        app = App.objects.filter(name=task_name).exists()

                        if not user:
                            user = Userapp.objects.create(username=request.user)
                            if not app:
                                ap = App.objects.create(name=task_name)
                                user.app.add(ap)
                            else:
                                ap = App.objects.get(name=task_name)
                                user.app.add(ap)
                            
                        else:
                            user = Userapp.objects.get(username=request.user)
                            if not app:
                                ap = App.objects.create(name=task_name)
                                user.app.add(ap)
                                
                            else:
                                ap = App.objects.get(name=task_name)
                                user.app.add(ap)
                                
                    else:
                        print(f"Task '{task_name}' failed")
        return JsonResponse({'message': 'Installation Successful'})
    except Exception as e:
        print("Installation Failed due to error:", str(e))
        return JsonResponse({'message': 'Installation Failed due to some error'})



@swagger_auto_schema(
    method='post',
    responses={
        200: openapi.Response(
            description='Deletion Successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                },
            ),
        ),
        400: openapi.Response(
            description='Deletion Failed',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
    }
)

@api_view(['POST'])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([TokenAuthentication])
def delete_environment(request):
    """
    Delete environment.

    This endpoint allows authenticated users to delete the environment using Ansible.

    ---
    # Response
    - `message` (string): Success or error message.
    """
    inventory_path = '/Users/rsah/Desktop/JetSetPack/jetsetpack/Ansible_create/inventory.ini'
    playbook_path = '/Users/rsah/Desktop/JetSetPack/jetsetpack/Ansible_delete/main.yml'
    host = 'client'

    try:
        options = {
            'inventory': inventory_path,
            'playbook': playbook_path,
        }
        run_ansible = ansible_runner.run(**options)
        for event in run_ansible.events:
            if event['event'] == 'runner_on_ok':
                result = event['event_data']
                t_name = result['task']
                task_status = result['res']['changed']
                if t_name == 'Gathering Facts':
                    pass
                else:
                    regex = re.compile(r"Uninstall\s+(.*)")
                    matches = regex.findall(t_name)
                    task_name = matches[0]
                    if task_status:
                        print(f"Task '{task_name}' was successful")
                        user = Userapp.objects.filter(username=request.user).exists()
                        if not user:
                            print("Invalid Authorization")
                        else:
                            user = Userapp.objects.get(username=request.user)
                            app = App.objects.filter(name=task_name).exists()
                            if not app:
                                print('Invalid app deletion')
                            else:
                                ap = App.objects.get(name=task_name)
                                user.app.remove(ap)

                    else:
                        print(f"Task '{task_name}' was not successful")

        return JsonResponse({'message': 'Deletion Successful'})
    except Exception as e:
        print("Uninstallation Failed due to error:", str(e))
        return JsonResponse({'message': 'Deletion Failed due to some error'})
    


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description='Successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'app_names': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING, description='App name'),
                    ),
                },
            ),
        ),
        400: openapi.Response(
            description='Error',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
    }
)

@api_view(['GET'])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_apps(request):
    """
    Get apps.

    This endpoint allows authenticated users to retrieve their associated apps.

    ---
    # Response
    - `app_names` (array of strings): Array of app names.
    """
    try:
        u = request.user
        user = Userapp.objects.filter(username=u).exists()
        if not user:
            return JsonResponse({'message':'User does not exists'})
        else:
            user = Userapp.objects.get(username=u)
            related_apps = user.app.all()
            app_names = [app.name for app in related_apps]
            for app_name in app_names:
                print(app_name)
            return JsonResponse({'app_names': app_names})
    except:
        return JsonResponse({'message':'Some error occured'})



@api_view(['POST'])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([TokenAuthentication])
def create_github_account(request):
    if request.method == 'POST':
        try:
            url = 'https://github.com/join' 
            return redirect(url)
        except:
            return JsonResponse({'message':'User is not authenticated'})
        


@api_view(['POST'])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([TokenAuthentication])
def create_slack_account(request):
    if request.method == 'POST':
        try:
            url = 'https://slack.com/signin#/signin' 
            return redirect(url)
        except:
            return JsonResponse({'message':'User is not authenticated'})




