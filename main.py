import hmac
import json
import os

import requests
from flask import abort

webhook_secret = bytes(os.environ['WEBHOOK_SECRET'], 'utf-8')
public_forward_url = os.environ.get('PUBLIC_FORWARD_URL')
private_forward_url = os.environ.get('PRIVATE_FORWARD_URL')


def github_hook(request):
    if request.method != 'POST':
        return abort(405)

    signature = request.headers.get('X-Hub-Signature')
    if signature is None:
        return abort(403)

    body = request.get_data()
    digest = hmac.new(webhook_secret, body, 'sha1').hexdigest()

    if not hmac.compare_digest('sha1=' + digest, signature):
        return abort(403)

    json_body = json.loads(body.decode('utf-8'))

    github_headers = {
        header: value
        for header, value in request.headers.items()
        if header.startswith('X-Github')
    }

    if public_forward_url and 'repository' in json_body and json_body['repository']['private'] is False:
        requests.post(public_forward_url, json=json_body, headers=github_headers)

    if private_forward_url:
        requests.post(private_forward_url, json=json_body, headers=github_headers)

    return 'OK'
