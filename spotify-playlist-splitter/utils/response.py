import json


def redirect(url: str, headers=None) -> dict:
    if headers is None:
        headers = {}

    headers['Location'] = url
    return response(302, headers)


def response(code: int = 200, headers=None, body=None):
    if body is None:
        body = {}
    if headers is None:
        headers = {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }
    return {
        'statusCode': code,
        'body': json.dumps(body),
        'headers': headers
    }
