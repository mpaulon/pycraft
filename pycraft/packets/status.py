import json

import pycraft.utils.formats as formats
import pycraft.utils.versions as versions
import pycraft.utils.hexprint as hexprint


def status(client):
    response = {
        "version": {
            # "name": versions.versions.get(client.proto_version),
            "name": "WTF protocol",
            "protocol": client.proto_version,
            # "protocol": 000,
        },
        "players": {
            "max": client.server.max_players,
            "online": client.server.online_players(),
            "sample":[], #TODO: return correct data about online players
        },
        "description": {
            "text": client.server.description,
        },
        # "favicon": client.server.favicon,

    }
    response_json = json.dumps(response)
    data = formats.varint_to_data(0b00) + formats.string_to_data(response_json)
    client.repl(data)

def pong(client, data):
    client.repl(formats.varint_to_data(0b01) + data)
    client.stop()