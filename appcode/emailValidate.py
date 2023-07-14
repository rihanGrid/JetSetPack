# import re
import requests
import json

# regex = r"^[a-zA-Z0-9_.+-]+@gmail.com$"

api_key = '302b6a7041174ab8973034f034e1d184';
api_url = 'https://emailvalidation.abstractapi.com/v1/?api_key=' + api_key

def is_valid_email(dataR):
    data = json.loads(dataR.decode('utf-8')) 
    if data['is_valid_format']['value'] and data['is_mx_found']['value'] and data['is_smtp_valid']['value']:
        if not data['is_catchall_email']['value'] and not data['is_role_email']['value'] and data['is_free_email']['value']:
            return True
    return False

def validate_email(email):
    print('email-->',email)
    response = requests.get(api_url + "&email="+ email)
    # print('Response---->',response.content)
    is_valid = is_valid_email(response.content)
    if not is_valid:
       return False
    else:
        return True

# def validate_email(email):
#     if not re.match(regex, email):
#         return False
#     return True