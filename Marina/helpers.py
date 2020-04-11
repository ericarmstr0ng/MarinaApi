import json

from flask import request, make_response
from google.auth.transport import requests
import constants
from constants import client_id, client_secret
from google.oauth2 import id_token

class Boat:
    def __init__(self, content):
        self.name = content["name"]
        self.type = content["type"]
        self.length = content["length"]
        self.owner = content["owner"]
        if 'loads' in content:
            self.loads = content["loads"]
        else:
            self.loads = []
        self.payload = {"name": self.name, "type": self.type, "length": self.length, "loads": self.loads, "owner": self.owner}

    def update_data(self):
        return self.payload

    def patch_data(self, content):
        if 'length' in content:
            self.length = content['length']
        if 'name' in content:
            self.name = content['name']
        if 'type' in content:
            self.type = content['type']
        self.payload = {"name": self.name, "type": self.type, "length": self.length, "loads": self.loads, "owner": self.owner}
    
    def remove_load(self, load_id):
        for i in range(len(self.loads)):
            if int(self.loads[i]['id']) == int(load_id):
                del self.loads[i]
                return True
            return False
            
    def display_loads(self, client):
        load_payload = []
        for cargo in self.loads:
            load_data = id_validator(client, cargo['id'], constants.loads)
            load = Load(load_data)
            load_payload.append(load.api_return(cargo['id']))
        return load_payload
        
    def html_return(self, boat_id):
        html = f"<ul>" \
               f"<li>ID: {boat_id}</li>" \
               f"<li>Name: {self.name}</li>" \
               f"<li>Type: {self.type}</li>" \
               f"<li>Length: {self.length}</li>" \
               f"<li>Self: {request.url_root}boats/{boat_id}</li>" \
               f"</ul>"
        return html


    def api_return(self, boat_id):
        self.payload["id"] = boat_id
        self.payload["self"] = f"{request.url_root}boats/{boat_id}"
        return self.payload


class Load:
    def __init__(self, content):
        self.weight = content["weight"]
        self.cargo = content["cargo"]
        self.delivery_date = content["delivery_date"]
        if 'carrier' in content and content['carrier']:
            self.carrier = content["carrier"]
        else:
            self.carrier = {}
        self.payload = {"weight": self.weight, "carrier": self.carrier, "delivery_date": self.delivery_date,
                        "cargo": self.cargo}

    def add_carrier(self, carrier):
        if self.carrier:
            return False
        self.carrier = carrier
        self.payload["carrier"] = self.carrier
        return True

    def remove_carrier(self):
        if not self.carrier:
            return False
        self.carrier = {}
        self.payload["carrier"] = self.carrier
        return True

    def update_data(self):
        return self.payload

    def api_return(self, load_id):
        self.payload["id"] = load_id
        self.payload["self"] = f"{request.url_root}loads/{load_id}"
        return self.payload


def id_validator(client, entity_id, kind):
    query = client.query(kind=kind)
    results = list(query.fetch())
    for e in results:
        if int(entity_id) == int(e.key.id_or_name):
            return e
    return None


def name_validator(client, content, kind, boat_id=None):
    query = client.query(kind=kind)
    results = list(query.fetch())
    if 'name' in content:
        name = content['name']
        for e in results:
            if name == e['name']:
                if boat_id != e.id:
                    return 'Boat name must be unique'
        if len(name) < 1 or len(name) > 20:
            return 'Name must be between 1 and 20 characters'
    if 'length' in content:
        length = content['length']
        if length < 0:
            return 'Length must be greater than 0'

    return False


def json_response(code, error_msg):
    res = make_response(json.dumps({'Error': error_msg}))
    res.mimetype = 'application/json'
    res.status_code = code
    return res


def update_entity(client, ent_id, ent_type, ent_object):
    with client.transaction():
        key = client.key(ent_type, int(ent_id))
        load = client.get(key)
        load.update(ent_object.update_data())
        client.put(load)



def unload_load(client, load_id):
    load_data = id_validator(client, load_id, constants.loads)
    if load_data:
        carrier_id = load_data['carrier']['id']
        if carrier_id:
            boat_data = id_validator(client, carrier_id, kind=constants.boats)
            boat = Boat(boat_data)
            if boat.remove_load(load_id):
                update_entity(client, carrier_id, constants.boats, boat)
        load = Load(load_data)
        load.remove_carrier()
        update_entity(client, load_id, constants.loads, load)


def verify():
    req = requests.Request()
    if not request.headers.get('Authorization'):
        return False
    bearer = request.headers.get('Authorization').replace('Bearer ', '')
    print (f'bearer is {bearer}')
    print(f'client_id is {client_id}')

    try:
        id_info = id_token.verify_oauth2_token( 
        bearer, req, client_id)
    except:
        return False
    print(id_info['name'])
    return id_info['sub']