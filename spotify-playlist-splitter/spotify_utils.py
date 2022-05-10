import base64
import json

import requests

from utils_secret import get_secret

# spotify endpoints
SPOTIFY_AUTH_BASE_URL = "https://accounts.spotify.com/{}"
SPOTIFY_AUTH_URL = SPOTIFY_AUTH_BASE_URL.format('authorize')
SPOTIFY_TOKEN_URL = SPOTIFY_AUTH_BASE_URL.format('api/token')

SCOPE = [
    'playlist-modify-public',
    'playlist-read-private',
    'playlist-modify-private',
    'user-read-recently-played',
    'user-top-read',
    'user-library-modify',
    'user-library-read',
    'ugc-image-upload'
]


def authorize(redirect_url, auth_token):

    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": redirect_url
    }

    spotify_credentials = json.loads(get_secret('SpotifyCredentials'))

    base64encoded = base64.b64encode(("{}:{}".format(spotify_credentials['id'], spotify_credentials['secret'])).encode())
    headers = {"Authorization": "Basic {}".format(base64encoded.decode())}

    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload,
                                 headers=headers)

    # tokens are returned to the app
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]

    return access_token
