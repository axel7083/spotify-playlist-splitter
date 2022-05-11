from utils.aws import get_api_gateway_endpoint
from utils.spotify import *
import urllib.parse
from utils.secret import *
from utils.response import response, redirect
from utils.decorators import cookie


def get_redirect_url() -> str:
    return "{url}callback".format(url=get_api_gateway_endpoint())


def auth():
    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": get_redirect_url(),
        "scope": ' '.join(SCOPE),
        "client_id": json.loads(get_secret('SpotifyCredentials'))['id']
    }

    url_args = "&".join(["{}={}".format(key, urllib.parse.quote(val))
                         for key, val in list(auth_query_parameters.items())])

    return redirect(url="{}/?{}".format(SPOTIFY_AUTH_URL, url_args))


def callback(event):
    if 'code' not in event['queryStringParameters']:
        return response(401)

    token = authorize(
        get_redirect_url(),
        event['queryStringParameters']['code'],
        json.loads(get_secret('SpotifyCredentials'))
    )

    # TODO: set expire date
    headers = {
        "Set-Cookie": f"token={token}; secure; httpOnly"
    }
    return redirect('/Prod/api/profile', headers)


@cookie()
def profile(token: str):
    return response(200, body={'user_id': get_user_id(token), 'playlists': fetch_all_playlists(token)})


@cookie()
def split_playlist(token: str):
    success = start_process(token)
    return response(200, body={'success': success})


def handle(event, context):
    if event['path'] == '/api/auth':
        return auth()

    if event['path'] == '/api/callback':
        return callback(event=event)

    if event['path'] == '/api/profile':
        return profile(event=event)

    if event['path'] == '/api/split-playlist':
        return split_playlist(event=event)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET'
        },
        'body': json.dumps(
            {'message': 'Hello world'}, default=str)
    }


def lambda_handler(event, context):
    return handle(event, context)

