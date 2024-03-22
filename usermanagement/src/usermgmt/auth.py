from functools import wraps
from flask import redirect, request, url_for, session, flash
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
import uuid
import json
import requests
from jose import jwt

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for session ID in Flask session or query parameters
        session_id = session.get('sessionId') or request.args.get('sessionId')

        if session_id is None:
            flash("Sorry, but you need to be logged in to access this page.")
            return redirect(url_for('landing', next=request.url))
        else:
            user_name = validate_session(session_id)
            if not user_name:
                flash("Sorry, but your session has timed out, please log in to access this page.")
                return redirect(url_for('landing', next=request.url))
            else:
                kwargs['username'] = user_name
        
        return f(*args, **kwargs)
    return decorated_function

def get_secret():
    secret_name = "StenoTechSecret"

    # Create a Secrets Manager client
    SMsession = boto3.session.Session()
    client = SMsession.client(
        service_name='secretsmanager',
        region_name='us-west-2'
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        # Handle the exception
        print(e)
        raise e
    else:
        # The secret value
        return json.loads(get_secret_value_response['SecretString'])

secretFromSM = get_secret()


def validate_session(session_id):

    if session_id is None:
        return False
    # Assume get_session_data() retrieves session data from DynamoDB
    session_data = get_session_data(session_id)  
    
    if not session_data:
        return False  # Session not found

    # Check if the custom session has expired
    if datetime.now().timestamp() > session_data['expiresAt']:
        return False  # Session has expired

    # Validate Cognito token
    keys = get_cognito_public_keys()
    token = session_data['additionalInfo']['EntireToken']['access_token']

    if not validate_cognito_token(token, keys):
        return False  # Cognito token is not valid
    
    return session_data['additionalInfo']['username']  # Session is valid

def get_session_data(session_id):

    dynamodb = boto3.resource('dynamodb')
    session_table = dynamodb.Table('UserSessionControl')

    response = session_table.query(
        KeyConditionExpression=Key('sessionId').eq(session_id)
    )
    items = response.get('Items', [])
    return items[0] if items else None

def validate_cognito_token(token, keys):
    try:
        # Decode and validate the token
        claims = jwt.decode(token, keys, algorithms=['RS256'], audience=secretFromSM['COGNITO_CLIENT_ID'])
        return claims is not None  # Token is valid
    except jwt.ExpiredSignatureError:
        return False  # Token is expired
    except jwt.JWTClaimsError:
        return False  # Token has invalid claims
    except Exception as e:
        print(f"Token validation error: {e}")
        return False

def get_cognito_public_keys():
    USER_POOL_ID = secretFromSM['USER_POOL_ID']
    url = f"https://cognito-idp.us-west-2.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
    response = requests.get(url)
    return response.json()

def exchange_code_for_token(code):
    redirectURL = request.host_url[:-1]
    if ('cloudfront' in redirectURL):
        redirectURL.replace("http://", "https://")

    CognitoDomain = secretFromSM['COGNITO_DOMAIN']
    CognitoClientID = secretFromSM['COGNITO_CLIENT_ID']
    token_url = f'{CognitoDomain}/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'client_id': CognitoClientID,
        'code': code,
        # 'redirect_uri': "http://localhost"+url_for('callback'),
        'redirect_uri': redirectURL+url_for('callback')

    }
    response = requests.post(token_url, headers=headers, data=data,)
    return response.json()

def create_user_session(user_id, additional_info):

    session_id = str(uuid.uuid4())
    expires_at = int((datetime.now() + timedelta(seconds=additional_info['tokenExpiration'])).timestamp())

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UserSessionControl')

    table.put_item(
        Item={
            'sessionId': session_id,
            'userId': user_id,
            'expiresAt': expires_at,
            'additionalInfo': additional_info
        }
    )
    return session_id