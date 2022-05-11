import base64
import json
from typing import Optional
import requests
import dateutil.parser
from io import BytesIO


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

spotify_color_dict = {
    '2018': {'background': (182, 154, 202), 'text': (254, 250, 63)},
    '2019': {'background': (241, 55, 166), 'text': (206, 245, 100)},
    '2020': {'background': (206, 245, 100), 'text': (204, 20, 131)},
    '2021': {'background': (208, 245, 106), 'text': (79, 51, 88)},
    '2022': {'background': (255, 210, 215), 'text': (233, 20, 42)},
}

params = {
    'limit': 50
}


def create_image(
        message: str,
        image_size: int,
        text_size: int,
        color_background: tuple[int, int, int],
        color_text: tuple[int, int, int]) -> str:
    """
    This function return a base64 encoded image with a text centred
    :param message: The text to place in the image
    :param image_size: The size (resolution) of the image (square)
    :param text_size: The size of the text
    :param color_background: The color of the background
    :param color_text: The color of the text
    :return:
    """
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (image_size, image_size), color=color_background)
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype('./data/GothamMedium.otf', text_size)
    w, h = d.textsize(message, font=fnt)
    d.text(((image_size-w)/2, (image_size-h)/2), message, font=fnt, fill=color_text)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def create_headers(token: str, base_header: dict[str, str] = None) -> dict[str, str]:
    header = {}
    if base_header is not None:
        header = base_header

    header['Authorization'] = f'Bearer {token}'
    return header


def authorize(redirect_url, auth_token, spotify_credentials: dict[str, str]):

    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": redirect_url
    }

    base64encoded = base64.b64encode(("{}:{}".format(spotify_credentials['id'], spotify_credentials['secret'])).encode())
    headers = {"Authorization": "Basic {}".format(base64encoded.decode())}

    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload,
                                 headers=headers)

    # tokens are returned to the app
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]

    return access_token


def fetch_items(url: str, token: str) -> [Optional[list], Optional[str]]:
    res = requests.get(
        url,
        headers=create_headers(token),
        params=params)
    if res.status_code != 200:
        return None, None
    return res.json()['items'], res.json()['next']


def fetch_all_playlists(token: str) -> Optional[dict[str, list]]:
    url_next = 'https://api.spotify.com/v1/me/playlists'
    playlists = {}

    while url_next is not None:
        i, url_next = fetch_items(url_next, token)
        if i is None:
            return None

        for playlist in i:
            playlists[playlist['name']] = playlist['id']

    return playlists


def set_playlist_image(token: str, playlist_id: str, message: str, image_size: int = 400, size: int = 120) -> bool:
    color_background = (41, 65, 171),
    color_text = (30, 215, 96)
    if message in spotify_color_dict:
        color_background = spotify_color_dict[message]['background']
        color_text = spotify_color_dict[message]['text']

    res = requests.put(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        data=create_image(message, image_size, size, color_background, color_text),
        headers=create_headers(token)
    )

    if res.status_code != 200 and res.status_code != 202:
        print(res.json())
        return False

    return True


def add_track_to_playlist(token: str, playlist_id: str, tracks: list[dict[str, str]]) -> bool:
    proceeded = 0

    while proceeded != len(tracks):
        buffer = tracks[proceeded:proceeded+100]
        res = requests.post(
            url=f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
            headers=create_headers(token),
            json={'uris': [track['uri'] for track in buffer]}
        )

        if res.status_code != 201:
            print(res.json())
            return False
        proceeded += len(buffer)
    return True


def get_user_id(token: str) -> Optional[str]:
    res = requests.get('https://api.spotify.com/v1/me', headers=create_headers(token))
    if res.status_code != 200:
        return None
    return res.json()['id']


def split_user_tracks_by_year(token: str) -> Optional[dict[str, list[dict[str, str]]]]:
    years = {}

    url_next = 'https://api.spotify.com/v1/me/tracks'
    tracks = []

    while url_next is not None:
        i, url_next = fetch_items(url_next, token)
        if i is None:
            return None
        tracks.extend(i)

    # For each track parse the added_at property
    for track in tracks:
        d = dateutil.parser.isoparse(track['added_at'])
        key = f'{d.year.real}'
        if key not in years:
            years[key] = []

        years[key].append({'uri': track['track']['uri'], 'name': track['track']['name'], 'added_at': track['added_at']})

    return years


def create_playlist(token:str, user_id: str, name: str) -> Optional[str]:
    res = requests.post(
        url=f'https://api.spotify.com/v1/users/{user_id}/playlists',
        headers=create_headers(token),
        json={'name': name, 'description': '', 'public': False}
    )

    if res.status_code != 201:
        print(res.json())
        return None

    _id = res.json()['id']
    print(f'playlist {name} created. id: {_id}')

    return _id


def start_process(token: str) -> bool:
    user_id = get_user_id(token)
    if user_id is None:
        return False

    playlists = fetch_all_playlists(token)
    if playlists is None:
        return False
    years = split_user_tracks_by_year(token)

    for (key, value) in sorted(years.items(), key=lambda k: int(k[0])):
        if key in playlists:
            continue

        playlist_id = create_playlist(token, user_id, key)
        if not set_playlist_image(token, playlist_id, key):
            return False

        if not add_track_to_playlist(token, playlist_id, value):
            return False
    return True
