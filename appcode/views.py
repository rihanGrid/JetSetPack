from .models import App, Userapp, AppName, Role, Auth
from django.http import JsonResponse
from .authentication import CustomIsAuthenticated, TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
import ansible_runner
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import redirect
from jetsetpack.settings import INVENTORY_PATH, CREATE, DELETE
import os
# import json
import base64
# from django.http import HttpResponse
from django.shortcuts import render
# import requests
# from django.core import serializers




@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['ip_address', 'os'],
        properties={
            'ip_address': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s IP address'),
            'os': openapi.Schema(type=openapi.TYPE_STRING, description='User\'s operating system (e.g., "MacOS")'),
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
        if os == "MacOS":
            inventory_line = f"{username}@{ip_address}"

            with open('Ansible_create/inventory.ini', 'w') as inventory_file:
                inventory_file.write(f"[client]\n{inventory_line}\n")


            return JsonResponse({'message': 'Inventory file created successfully'})
        elif os == "Windows":
            pass
        elif os == "CentOS":
            pass
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
    # Request Body
    - `roles` (string): User's role address.
    # Response
    - `message` (string): Success or error message.
    """
    inventory_path = INVENTORY_PATH
    playbook_path = CREATE
    hosts = 'client'
    roles = request.data.get('roles')

    try:
        options = {
            'inventory': inventory_path,
            'playbook': playbook_path,
            'extravars': {'hosts': hosts, 'roles': roles}
        }

        r = ansible_runner.run(**options)
        res = {}
        for event in r.events:
            if event['event'] == 'runner_on_ok':
                result = event['event_data']

                t_name = result['task']
                task_status = result['res']['changed']
                if t_name == 'Gathering Facts':
                    pass
                else:
                    matches = t_name.split()
                    task_name = matches[1]
                    print(task_name)
                    if task_status:
                        data = {task_name:"Suscessful"}
                        res.update(data)
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
                        data = {task_name:"Already Exists"}
                        res.update(data)
                        print(f"Task '{task_name}' already exists")
            # if event['event'] == 'runner_on_failed':
            #     result = event['event_data']
            #     t_name = result['task']
            #     error_msg = result['res']['msg']
            #     print(f"Task '{t_name}' failed with error: {error_msg}")
        return JsonResponse({'message': 'Installation Successful', 'data':res})
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
    inventory_path = INVENTORY_PATH
    playbook_path = DELETE
    hosts = 'client'
    roles = request.data.get('roles')

    try:
        options = {
            'inventory': inventory_path,
            'playbook': playbook_path,
            'extravars': {'hosts': hosts, 'roles': roles}
        }
        run_ansible = ansible_runner.run(**options)
        res = {}
        for event in run_ansible.events:
            if event['event'] == 'runner_on_ok':
                result = event['event_data']
                t_name = result['task']
                task_status = result['res']['changed']
                if t_name == 'Gathering Facts':
                    pass
                else:
                    matches = t_name.split()
                    task_name = matches[1]
                    print(task_name)
                    if task_status:
                        data = {task_name:"Suscessful"}
                        res.update(data)
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
                        data = {task_name:"Doesn't Exists"}
                        res.update(data)
                        print(f"Task '{task_name}' was not successful")
        return JsonResponse({'message': 'Deletion Successful', 'data': res})
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
def create_role(request):
    try:
        role_name = request.data.get('role')
        if Role.objects.filter(name=role_name).exists():
            return JsonResponse({'message':'Role already exists'})
        else:
           role = Role.objects.create(name=role_name)
           return JsonResponse({'message':'Role added Suscessfully'})
    except Exception as e:
        print('Uninstallation Failed due to error:', str(e))
        return JsonResponse({'message':'Some error occured'})


@api_view(['POST'])
def create_app(request):
    try:
        role_name = request.data.get('role')
        app_name = request.data.get('app')
        if Role.objects.filter(name=role_name).exists():
            if AppName.objects.filter(name=app_name).exists():
                ro = Role.objects.get(name = role_name)
                ap = AppName.objects.get(name=app_name)
                ro.apps.add(ap)
                return JsonResponse({'message':'Apps added Suscessfully'})
            else:
                ro = Role.objects.get(name = role_name)
                ap = AppName.objects.create(name = app_name)
                ro.apps.add(ap)
                return JsonResponse({'message':'Apps added Suscessfully'})
        else:
            return JsonResponse({'message':'Role does not exist'})
    except Exception as e:
        print('Uninstallation Failed due to error:', str(e))
        return JsonResponse({'message':'Some error occured'})



@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'role',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Role name',
        ),
    ],
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
def get_role_apps(request):
    try:
        role_name = request.data.get('role')
        if Role.objects.filter(name=role_name).exists():
            role = Role.objects.get(name = role_name)
            related_apps = role.apps.all()
            app_names = [app.name for app in related_apps]
            for app_name in app_names:
                print(app_name)
            return JsonResponse({'app_names': app_names})
        else:
            return JsonResponse({'message':'Invalid Role'})
    except Exception as e:
        print('Fetching of data failed due to error:', str(e))
        return JsonResponse({'message':'Some error occured'})




@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'role_name',
            openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description='Role name',
        ),
    ],
    responses={
        200: openapi.Response(
            description='Successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'images': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING, format='binary', description='Base64-encoded image data'),
                    ),
                },
            ),
        ),
        400: openapi.Response(
            description='Error',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
    }
)

@api_view(['GET'])
def get_images(request, role_name):
    try:
        folder_path = os.path.join('images', role_name)
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return JsonResponse({'error': 'Invalid folder name'}, status=400)
        
        image_files = []
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.jpg') or file_name.endswith('.png'):
                image_files.append(os.path.join(folder_path, file_name))
                # print("file name--->",file_name)
        print("No of images---->", len(image_files))
        
        images_data = []
        for image_file in image_files:
            print("image file name----->",image_file[15:(len(image_file)-4)])
            with open(image_file, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                # images_data.append(base64_data)
                images_data.append({image_file[15:(len(image_file)-4)]:base64_data})
        print("size of image is ----->",len(image_data))
        
        return JsonResponse({'images': images_data}, status=200)
    except Exception as e:
        print('Fetching of data failed due to error:', str(e))
        return JsonResponse({'message':'Some error occurred'})


# @api_view(['GET'])
# def get_images(request,role_name):
#     try:
#         folder_path = os.path.join('images', role_name)
#         if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
#             return JsonResponse({'error': 'Invalid folder name'}, status=400)
#         image_files = []
#         for file_name in os.listdir(folder_path):
#             if file_name.endswith('.jpg') or file_name.endswith('.png'):
#                 image_files.append(os.path.join(folder_path, file_name))
#         response = HttpResponse(content_type='application/octet-stream')
#         for image_file in image_files:
#             with open(image_file, 'rb') as f:
#                 response.write(f.read())
        
#         return response
#     except Exception as e:
#         print('Fetching of data failed due to error:', str(e))
#         return JsonResponse({'message':'Some error occured'})

# @api_view(['GET'])
# def get_images(request, role_name):
#     try:
#         folder_path = os.path.join('images', role_name)
#         if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
#             return JsonResponse({'error': 'Invalid folder name'}, status=400)
        
#         image_files = []
#         for file_name in os.listdir(folder_path):
#             if file_name.endswith('.jpg') or file_name.endswith('.png'):
#                 image_files.append(os.path.join(folder_path, file_name))
        
#         response = HttpResponse(content_type='image/jpeg')  # Adjust content-type based on your image format
        
#         for image_file in image_files:
#             with open(image_file, 'rb') as f:
#                 response.write(f.read())
        
#         return response
    
#     except Exception as e:
#         print('Fetching of data failed due to error:', str(e))
#         return JsonResponse({'message': 'Some error occurred'})



@api_view(['GET'])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_profile(request):
    try:
        u = request.user
        user = Auth.objects.filter(username=u).exists()
        if user:
            a = Auth.objects.get(username=u)
            uname = a.username
            email = a.email
            temp = {'username':uname, 'email':email}
            return JsonResponse({'data':temp}, status=200)
        else:
            return JsonResponse({'message':'User doesn\'t exist'}, status=400)
    except Exception as e:
        return JsonResponse({'message':'Some unknown exception occured'}, status=400)




@api_view(['GET'])
def create_github_account(request):
    if request.method == 'GET':
        url = 'https://github.com/join' 
        return redirect(url)
        


@api_view(['GET'])
def create_slack_account(request):
    if request.method == 'GET':
        url = 'https://slack.com/signin#/signin' 
        return redirect(url)
    

@api_view(['POST'])
@permission_classes([CustomIsAuthenticated])
@authentication_classes([TokenAuthentication])
def set_single_app(request,app_name):
    inventory_path = INVENTORY_PATH
    playbook_path = CREATE
    hosts = 'client'
    roles = app_name

    try:
        options = {
            'inventory': inventory_path,
            'playbook': playbook_path,
            'extravars': {'hosts': hosts, 'roles': roles}
        }

        r = ansible_runner.run(**options)
        res = {}
        for event in r.events:
            if event['event'] == 'runner_on_ok':
                result = event['event_data']

                t_name = result['task']
                task_status = result['res']['changed']
                if t_name == 'Gathering Facts':
                    pass
                else:
                    matches = t_name.split()
                    task_name = matches[1]
                    print(task_name)
                    if task_status:
                        data = {task_name:"Suscessful"}
                        res.update(data)
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
                        data = {task_name:"Already Exists"}
                        res.update(data)
                        print(f"Task '{task_name}' already exists")
        return JsonResponse({'data':res})
    except Exception as e:
        print("Installation Failed due to error:", str(e))
        return JsonResponse({'message': 'Installation Failed due to some error'})

