import json
import os


def get_secret(id):
    if os.path.isfile("client_secrets.json"):
        secrets = json.loads(open("client_secrets.json").read())
        return secrets[id]
    else:
        raise OSError("No secrets file.")
