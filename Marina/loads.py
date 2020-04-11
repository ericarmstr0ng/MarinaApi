from flask import Blueprint, request, jsonify
from google.cloud import datastore
import json
import constants
from jsonschema import validate
from helpers import id_validator
from helpers import Load, unload_load,json_response, verify

import os

# os.environ[
#     "GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/IngloriousLoki/Desktop/Cloud/Marina/project-loki-0c4fe8ce166f.json"

client = datastore.Client()
bp = Blueprint('loads', __name__, url_prefix='/loads')


@bp.errorhandler(404)
def resource_not_found_404(e):
    return jsonify(Error=str(e)), 404


@bp.errorhandler(400)
def resource_not_found_400(e):
    return jsonify(Error=str(e)), 400


@bp.errorhandler(403)
def resource_not_found_403(e):
    return jsonify(Error=str(e)), 403


@bp.route('', methods=['POST'])
def loads_post():
    content = request.get_json()
    try:
        validate(instance=content, schema=constants.loads_schema)
    except:
        return resource_not_found_400("The request object is missing at least one of the required attributes")

    new_load = datastore.entity.Entity(key=client.key(constants.loads))
    payload = Load(content)
    new_load.update(payload.update_data())
    client.put(new_load)
    return jsonify(payload.api_return(new_load.id)), 201


@bp.route('/<load_id>', methods=['GET'])
def loads_get_id(load_id):
    load = id_validator(client, load_id, constants.loads)
    if load:
        payload = Load(load)
        return jsonify(payload.api_return(load_id))
    return resource_not_found_404("No load with this load_id exists")


@bp.route('', methods=['GET'])
def loads_get():
    payload = []
    query = client.query(kind=constants.loads)
    q_limit = int(request.args.get('limit', '5'))
    q_offset = int(request.args.get('offset', '0'))
    l_iterator = query.fetch(limit=q_limit, offset=q_offset)
    pages = l_iterator.pages
    results = list(next(pages))
    if l_iterator.next_page_token:
        next_offset = q_offset + q_limit
        next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
    else:
        next_url = None
    for e in results:
        e["id"] = e.key.id
        load_data = id_validator(client, e.key.id, constants.loads)
        load = Load(load_data)
        payload.append(load.api_return(e.key.id))
    output = {constants.loads: payload}
    if next_url:
        output["next"] = next_url
    return jsonify(output)


@bp.route('<load_id>', methods=['DELETE'])
def loads_delete(load_id):
    load = id_validator(client, load_id, constants.loads)
    if load:
        if load['carrier']:
            unload_load(client, load_id)
            key = client.key(constants.loads, int(load_id))
            client.delete(key)
        return '', 204
    return resource_not_found_404("No load with this load_id exists")


@bp.route('<load_id>', methods=['PATCH'])
def loads_unload(load_id):
    owner = verify()
    if not owner:
        return json_response(401, error_msg='Invalid JWT')
    load = id_validator(client, load_id, constants.loads)
    if load:
        unload_load(client, load_id)
        return '', 204
    return resource_not_found_404("No load with this load_id exists")
