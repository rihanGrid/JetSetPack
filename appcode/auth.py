from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from .authSerializers import AuthSerializer
from .models import Auth
from passlib.hash import pbkdf2_sha256
from django.db.models import Q
import jwt
import datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .emailValidate import validate_email


JWT_SECRET = 'griddynamics'




@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        },
        required=['username', 'email', 'password'],
    ),
    responses={
        201: openapi.Response(
            description='User Created',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT token'),
                    'statusText': openapi.Schema(type=openapi.TYPE_STRING, description='Status text'),
                },
            ),
        ),
        400: openapi.Response(
            description='Bad Request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
        409: openapi.Response(
            description='Conflict',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
        500: openapi.Response(
            description='Internal Server Error',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
    }
)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    User signup.

    This endpoint allows users to sign up by providing their username, email, and password.

    ---
    # Request Body
    - `username` (string, required): Username of the user.
    - `email` (string, required): Email address of the user.
    - `password` (string, required): Password of the user.

    # Response
    - `token` (string): JWT token for authentication.
    - `statusText` (string): Status text indicating the user creation.
    """
    try:
        data = request.data if request.data is not None else {}
        required_fields = set(['username', 'email', 'password'])
        if not required_fields.issubset(data.keys()):
            return Response(status=400, data={'error': 'Missing required fields'})
        existing_user = Auth.objects.filter(Q(username=data['username']) | Q(email=data['email']))
        if existing_user:
            return Response(status=409, data={'error': 'User with the same username or email already exists'})
        # email_validate = data['email']
        # check = validate_email(email_validate)
        # if check is False:
        #     return Response({'message':'Email you entered is invalid'})
        password_hash = pbkdf2_sha256.hash(data['password'])
        user = {
            'username': data['username'],
            'email': data['email'],
            'password': str(password_hash)
        }
        serializer = AuthSerializer(data=user)
        if serializer.is_valid():
            instance = serializer.save()
        token = jwt.encode(
            {'username': data['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, JWT_SECRET)
        return Response(status=status.HTTP_201_CREATED, data={'token': token, 'statusText': 'User Created'})

    except Exception as e:
        return Response(status=500, data={'error': str(e)})




@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        },
        required=['username', 'password'],
    ),
    responses={
        200: openapi.Response(
            description='Success',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT token'),
                },
            ),
        ),
        400: openapi.Response(
            description='Bad Request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
        401: openapi.Response(
            description='Unauthorized',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
        500: openapi.Response(
            description='Internal Server Error',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
    }
)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    User login.

    This endpoint allows users to log in by providing their username and password.

    ---
    # Request Body
    - `username` (string, required): Username of the user.
    - `password` (string, required): Password of the user.

    # Response
    - `token` (string): JWT token for authentication.
    """
    try:
        data = request.data if request.data is not None else {}
        required_fields = set(['username', 'password'])
        if not required_fields.issubset(data.keys()):
            return Response(status=400, data={'error': 'Missing required fields'})

        user = Auth.objects.get(username=data['username'])
        print(user)
        if user and pbkdf2_sha256.verify(data['password'], user.password):
            token = jwt.encode(
                {'username': user.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10)},
                JWT_SECRET)
            return Response(status=200, data={'token': token})
        else:
            return Response(status=401, data={'error': 'Invalid username or password'})

    except Exception as e:
        return Response(status=500, data={'error': str(e)})




@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='Old password'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
        },
        required=['username', 'old_password', 'new_password'],
    ),
    responses={
        200: openapi.Response(
            description='Success',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                },
            ),
        ),
        400: openapi.Response(
            description='Bad Request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
        401: openapi.Response(
            description='Unauthorized',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
        404: openapi.Response(
            description='Not Found',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
        500: openapi.Response(
            description='Internal Server Error',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                },
            ),
        ),
    }
)

@api_view(['PUT'])
def changePassword(request):
    """
    Change user password.

    This endpoint allows users to change their password by providing the old and new passwords.

    ---
    # Request Body
    - `username` (string, required): Username of the user.
    - `old_password` (string, required): Old password of the user.
    - `new_password` (string, required): New password for the user.

    # Response
    - `message` (string): Success message indicating that the password was updated successfully.
    """
    try:
        data = request.data if request.data is not None else {}
        required_fields = set(['username', 'old_password', 'new_password'])
        if not required_fields.issubset(data.keys()):
            return Response(status=400, data={'error': 'Missing required fields'})
        user = Auth.objects.get(username=data['username'])
        if not user:
            return Response(status=404, data={'error': 'User not found'})
        if not pbkdf2_sha256.verify(data['old_password'], user.password):
            return Response(status=401, data={'error': 'Invalid old password'})
        new_password_hash = pbkdf2_sha256.hash(data['new_password'])
        user.password = new_password_hash
        user.save()
        return Response(status=200, data={'message': 'Password updated successfully'})
    except Exception as e:
        return Response(status=500, data={'error': str(e)})
