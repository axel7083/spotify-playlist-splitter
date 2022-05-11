from functools import wraps
from http.cookies import SimpleCookie

from .response import response, redirect


def cookie():
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            if 'event' not in kwargs:
                raise Exception("The headers property must be sent as positional argument.")
            event = kwargs['event']

            if 'headers' not in event:
                return response(401)

            if 'Cookie' not in event['headers']:
                return redirect('/Prod/api/auth')

            _cookie = SimpleCookie()
            _cookie.load(event['headers']['Cookie'])

            if 'token' not in _cookie:
                return redirect('/Prod/api/auth')

            kwargs['token'] = _cookie.get('token').value
            kwargs.pop('event')
            return fun(*args, **kwargs)
        return wrapper
    return decorator
