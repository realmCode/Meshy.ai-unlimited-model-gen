import os
import hashlib
import base64
import json
from icecream import ic

def hsh():
    data = os.urandom(32).hex().encode('utf-8')
    hash_bytes = hashlib.sha256(data).digest()
    b64 = base64.urlsafe_b64encode(hash_bytes).rstrip(b'=')
    return b64.decode('utf-8')

def save(email, data):
    accounts = {}

    # If file exists and is not empty, load existing data
    if os.path.exists("accounts.json") and os.path.getsize("accounts.json") > 0:
        with open("accounts.json", "r") as f:
            try:
                accounts = json.load(f)
            except json.JSONDecodeError:
                accounts = []

    # Append new account
    accounts.update({email: data})

    # Overwrite the file with updated data
    with open("accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)