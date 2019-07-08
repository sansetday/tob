import json
from pprint import pprint


# class ResponseMask


class Server:
    def __init__(self, address, need_auth, api_key, request_mask, response_mask):
        self.address = address
        self.need_auth = need_auth
        self.api_key = api_key
        self.request_mask = request_mask
        self.response_mask = response_mask


def getServers(file_name):
    with open(file_name) as f:
        data = json.load(f)
        #pprint((data['servers'][0]['address']))  # для теста

    servers = [Server(s['address'], s['need_auth'], s['api_key'], s['request_mask'], s['response_mask'])
               for s in data['servers']]
    list()
    return servers


if __name__ == '__main__':
    servers = getServers('ipservers.json')
    pprint(servers[0].response_mask)  # для теста

