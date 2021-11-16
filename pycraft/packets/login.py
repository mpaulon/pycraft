import secrets

from hashlib import sha1

import pycraft.utils.formats as formats
import pycraft.utils.cryptography as cryptography

CLIENT_AUTH_URL = "https://sessionserver.mojang.com/session/minecraft/hasJoined?username={username}&serverId={serverId}"#&ip={ip}"




def encryption_request(client):
    server_id = formats.string_to_data(client.server.id)
    pkey_data = formats.varint_to_data(len(client.server.public_key)) + client.server.public_key
    verify_token_data = formats.varint_to_data(len(client.verify_token)) + client.verify_token
    data = server_id + pkey_data + verify_token_data

    client.repl(formats.varint_to_data(0x01) + data)

def login_success(client, data):
    shared_secret_len, next_byte = formats.varint_from_data(data)
    shared_secret = cryptography.decode_with_privkey(
        data[next_byte: next_byte+shared_secret_len], 
        client.server.private_key["d"], 
        client.server.private_key["n"]
    )
    verify_token_len, next_byte = formats.varint_from_data(data, next_byte+shared_secret_len)
    verify_token = cryptography.decode_with_privkey(
        data[next_byte: next_byte+verify_token_len], 
        client.server.private_key["d"], 
        client.server.private_key["n"]
    )
    if client.verify_token != verify_token:
        client.close()
        raise RuntimeError("Invalid verify token")

    client.shared_secret = shared_secret

    server_id = sha1()
    server_id.update(client.server.id.encode())
    server_id.update(shared_secret)
    server_id.update(client.server.public_key)

  
    data = ""
    client.repl(data)