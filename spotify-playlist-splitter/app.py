from http.cookies import SimpleCookie
from aws_utils import get_api_gateway_endpoint
from spotify_utils import *
import urllib.parse
from utils_secret import get_secret


def get_redirect_url() -> str:
    return "{url}callback".format(url=get_api_gateway_endpoint())


def response(code: int = 200, headers=None, body: str = json.dumps({})):
    if headers is None:
        headers = {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }

    return {
        'statusCode': code,
        'body': body,
        'headers': headers
    }


def auth():
    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": get_redirect_url(),
        "scope": ' '.join(SCOPE),
        "client_id": json.loads(get_secret('SpotifyCredentials'))['id']
    }

    url_args = "&".join(["{}={}".format(key, urllib.parse.quote(val))
                         for key, val in list(auth_query_parameters.items())])

    return response(302, {'Location': "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)})


def callback(event):
    if 'code' not in event['queryStringParameters']:
        return response(401)

    token = authorize(get_redirect_url(), event['queryStringParameters']['code'])
    # TODO: set expire date
    headers = {
        "Set-Cookie": f"token={token}; secure; httpOnly"
    }
    return response(200, headers)


def profile(event):
    if 'Cookie' not in event['headers']:
        return response(401, body="Missing token")
    cookie = SimpleCookie()
    cookie.load(event['headers']['Cookie'])

    if 'token' not in cookie:
        return response(401, body="Missing token")

    return response(200, body=f'token cookie equal to {cookie.get("token").value}')


def handle(event, context):
    if event['path'] == '/api/auth':
        return auth()

    if event['path'] == '/api/callback':
        return callback(event)

    if event['path'] == '/api/profile':
        return profile(event)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(
            {'message': event}, default=str)
    }


def lambda_handler(event, context):
    return handle(event, context)

