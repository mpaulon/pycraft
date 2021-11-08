import pycraft.utils.formats as formats

def encryption_request(client):
    server_id = formats.string_to_data(client.server.id)
    pkey_data = formats.varint_to_data(len(self.server.public_key))
  
    data = ""
    client.repl(data)