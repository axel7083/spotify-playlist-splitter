# Spotify Playlist Splitter

This AWS Lambda Function provide a simple API for splitting user's tracked song in yearly based playlists.

# Endpoints

It provides 4 endpoints

| Endpoint            | HTTP Method | Description                                                      |
|---------------------|-------------|------------------------------------------------------------------|
| /api/auth           | GET         | This url will redirect the user to the Spotify login page        |
| /api/callback       | GET         | This url is used by spotify to redirect a user after he signs in |
| /api/profile        | GET         | This url will list the user's playlists name and ids             |
| /api/split-playlist | GET         | This url will split the user's tracked song in yearly playlists  |

Sadly it appears we cannot put a different timeout on different events for the API gateway using the `template.yaml`: [Cannot set Api Event function timeout](https://github.com/aws/serverless-application-model/issues/1701)

To use the `/api/split-playlist` endpoint, we need to change the default timeout (Put 20000).

# Secrets management

In order to use this function, you need to create an AWS Secret, with 2 keys value `id` and `secret`, corresponding to your Spotify Application credentials.

Once it is created and deployed on the same AWS::Region as your function, change in `template.yaml` the `AWSSecretsManagerGetSecretValuePolicy` arn.