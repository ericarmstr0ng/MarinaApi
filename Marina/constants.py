loads = "loads"
boats = "boats"
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email']
API_SERVICE_NAME = 'people'
API_VERSION = 'v1'
client_id = r'840256517736-4hk5lqkh1f6h2iepj0gd86m37m19ncc3.apps.googleusercontent.com'
client_secret = r'Z3hxoIlzxp1WHHz6Rr2cCin6'

boats_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "type": {"type": "string"},
        "length": {"type": "number"},
    },
    "additionalProperties": False,
    "required": ["name", "type", "length"]
}

patch_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "type": {"type": "string"},
        "length": {"type": "number"},
    },
    "additionalProperties": False,
}


loads_schema = {
    "type": "object",
    "properties": {
        "weight": {"type": "number"},
        "cargo": {"type": "string"},
        "delivery_date": {"type": "string"},
    },
    "additionalProperties": False,
    "required": ["weight", "cargo", "delivery_date"]
}

load_boat_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
    },
    "additionalProperties": False,
    "required": ["id"]
}
