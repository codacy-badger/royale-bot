from discord import *

def admin_get(self):
    return self.server_permissions.administrator

Member.admin = property(admin_get)

def dict_get(self):
    data = {}
    data['message_id'] = getattr(self,'id',None)
    channel = getattr(self,'channel',None)
    if channel != None:
        data['channel_id'] = getattr(channel,'id',None)
    else:
        data['channel_id'] = None
    return data

Message.id_dict = property(dict_get)

def in_server(self,serverid):
    found = False
    for server in self.servers:
        if server.id == serverid:
            found = True
            break
    return found

Client.in_server = property(in_server)
