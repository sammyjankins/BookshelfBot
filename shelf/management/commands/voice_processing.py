import json
import os

import requests

import shelf.management.commands.secrets


def recognize(file_path):
    with open(file_path, "rb") as f:
        data_sound = f.read()
    os.remove(file_path)
    headers = {'Authorization': f'Bearer {create_token(shelf.management.commands.secrets.YANDEX_OAUTH)[0]}'}

    params = {
        'lang': 'ru-RU',
        'folderId': shelf.management.commands.secrets.YANDEX_FOLDER_ID,
        'sampleRateHertz': 48000,
    }

    response = requests.post(shelf.management.commands.secrets.URL_REC, params=params, headers=headers, data=data_sound)
    decode_resp = response.content.decode('UTF-8')
    text = json.loads(decode_resp)

    return text


def synthesize(text, file_path):
    headers = {'Authorization': f'Bearer {create_token(shelf.management.commands.secrets.YANDEX_OAUTH)[0]}'}
    params = {
        'text': text,
        'lang': 'ru-RU',
        'folderId': shelf.management.commands.secrets.YANDEX_FOLDER_ID,
        'voice': 'ermil',
    }

    response = requests.post(shelf.management.commands.secrets.URL_SYNTH, params=params, headers=headers)
    with open(file_path, mode='wb') as file:
        file.write(response.content)


def create_token(oauth_token):
    params = {'yandexPassportOauthToken': oauth_token}
    response = requests.post(shelf.management.commands.secrets.YA_TOKEN_REFRESH_URL, params=params)
    decode_response = response.content.decode('UTF-8')
    text = json.loads(decode_response)
    iam_token = text.get('iamToken')
    expires_iam_token = text.get('expiresAt')

    return iam_token, expires_iam_token
