from flask import Blueprint, request, jsonify, make_response
from google.cloud import datastore
import json
import constants
from jsonschema import validate
from helpers import id_validator, name_validator
from helpers import Boat, Load, update_entity, unload_load, json_response, verify

import os

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/IngloriousLoki/Desktop/Cloud/Marina/project-loki-0c4fe8ce166f.json"

client = datastore.Client()
bp = Blueprint('boats', __name__, url_prefix='/boats')


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
def boats_post():
    owner = verify()
    if not owner:
        return json_response(401, error_msg='Invalid JWT')
    if 'application/json' in request.content_type:
        content = request.get_json()
        try:
            validate(instance=content, schema=constants.boats_schema)
        except:
            return resource_not_found_400("The request object is missing at least one of the required attributes")
        if 'application/json' not in request.accept_mimetypes:
            return json_response(406, error_msg='Content must be returned in JSON format')
        error_msg = name_validator(client, content, constants.boats)
        if not error_msg:
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            content['owner'] = owner
            payload = Boat(content)
            new_boat.update(payload.update_data())
            client.put(new_boat)
            return jsonify(payload.api_return(new_boat.id)), 201
        elif 'unique' in error_msg:
            return json_response(403, error_msg=f'{error_msg}')
        else:
            return json_response(400, error_msg=f'{error_msg}')

    return json_response(400, error_msg='Body must be in JSON format')
    # if 'application/json' in request.content_type:
    #     content = request.get_json()
    #     try:
    #         validate(instance=content, schema=constants.boats_schema)
    #     except:
    #         return resource_not_found_400("The request object is missing at least one of the required attributes")
    #     if 'application/json' not in request.accept_mimetypes:
    #         return json_response(406, error_msg='Content must be returned in JSON format')
    #     error_msg = name_validator(client, content, constants.boats)
    #     if not error_msg:
    #         new_boat = datastore.entity.Entity(key=client.key(constants.boats))
    #         payload = Boat(content)
    #         new_boat.update(payload.update_data())
    #         client.put(new_boat)
    #         return jsonify(payload.api_return(new_boat.id)), 201
    #     elif 'unique' in error_msg:
    #         return json_response(403, error_msg=f'{error_msg}')
    #     else:
    #         return json_response(400, error_msg=f'{error_msg}')

    # return json_response(400, error_msg='Body must be in JSON format')


@bp.route('/<boat_id>', methods=['PATCH'])
def boats_patch(boat_id):
    owner = verify()
    if not owner:
        return json_response(401, error_msg='Invalid JWT')
    if 'application/json' in request.accept_mimetypes:
        boat_data = id_validator(client, boat_id, constants.boats)
        if boat_data:
            content = request.get_json()
            try:
                validate(instance=content, schema=constants.patch_schema)
            except:
                return resource_not_found_400("The request object has incorrect attributes")
            boat = Boat(boat_data)
            boat.patch_data(content)
            error_msg = name_validator(client, content, constants.boats, boat_id)
            if error_msg:
                return json_response(403, error_msg=f'{error_msg}')
            update_entity(client, boat_id, constants.boats, boat)
            return jsonify(boat.api_return(boat_id))

        return resource_not_found_404("No boat with this boat_id exists")
    return json_response(406, error_msg='Content must be in JSON format')


# @bp.route('/<boat_id>', methods=['PUT'])
# def boats_put(boat_id):
#     if 'application/json' in request.content_type:
#         boat_data = id_validator(client, boat_id, constants.boats)
#         if boat_data:
#             content = request.get_json()
#             try:
#                 validate(instance=content, schema=constants.boats_schema)
#             except:
#                 return resource_not_found_400("The request object has incorrect attributes")
#             boat = Boat(content)
#             error_msg = name_validator(client, content, constants.boats, boat_id)
#             if not error_msg:
#                 update_entity(client, boat_id, constants.boats, boat)
#                 response = jsonify(boat.api_return(boat_id))
#                 response.status_code = 303
#                 response.headers['Location'] = f"{boat.api_return(boat_id)['self']}"
#                 return response
#             return json_response(403, error_msg='Boat name must be unique')
#         return resource_not_found_404("No boat with this boat_id exists")
#     return json_response(406, error_msg='Content must be in JSON format')


@bp.route('<boat_id>', methods=['GET'])
def boats_get_boat(boat_id):
    if 'application/json' in request.accept_mimetypes:
        boat_data = id_validator(client, boat_id, constants.boats)
        if boat_data:
            boat = Boat(boat_data)
            if 'application/json' in request.accept_mimetypes:
                return jsonify(boat.api_return(boat_id))
            else:
                return json_response(406, error_msg='Content must be in JSON or HTML format')
        return json_response(404, error_msg='No boat with this boat_id exists')
    return json_response(406, error_msg='Content must be in JSON format')

@bp.route('', methods=['GET'])
def boats_get():
    if 'application/json' in request.accept_mimetypes:
        payload = []
        query = client.query(kind=constants.boats)
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
            boat_data = id_validator(client, e.key.id, constants.boats)
            boat = Boat(boat_data)
            payload.append(boat.api_return(e.key.id))
            output = {constants.boats: payload}
        if next_url:
            output["next"] = next_url
        return jsonify(output)
    return json_response(406, error_msg='Content must be in JSON format')
    

@bp.route('/<boat_id>/loads', methods=['GET'])
def boats_get_loads(boat_id):
    if 'application/json' in request.accept_mimetypes:
        boat_data = id_validator(client, boat_id, constants.boats)
        if boat_data:
            boat = Boat(boat_data)
            return jsonify(boat.display_loads(client))
        return resource_not_found_404("No boat with this boat_id exists")
    return json_response(406, error_msg='Content must be in JSON format')

@bp.route('<boat_id>', methods=['PUT'])
def load_cargo(boat_id):
    owner = verify()
    if not owner:
        return json_response(401, error_msg='Invalid JWT')
    if 'application/json' in request.accept_mimetypes:
        content = request.get_json()
        try:
            validate(instance=content, schema=constants.load_boat_schema)
        except:
            return resource_not_found_400("The request object is missing at least one of the required attributes")
        load_id = content["id"]
        boat_data = id_validator(client, boat_id, kind=constants.boats)
        load_data = id_validator(client, load_id, kind=constants.loads)
        if boat_data and load_data:
            if not load_data["carrier"]:
                boat = Boat(boat_data)
                load_carrier = {"id": load_id, "self": f"{request.url_root}loads/{load_id}"}
                load = Load(load_data)
                boat_carrier = {"id": boat_id, "name": boat_data["name"], "self": f"{request.url_root}/boats/{boat_id}"}
                load.add_carrier(boat_carrier)
                boat.loads.append(load_carrier)
                update_entity(client, boat_id, constants.boats, boat)
                update_entity(client, load_id, constants.loads, load)
                return json_response(204,error_msg='OK')
            return resource_not_found_400("Load already assigned to a boat")
        return resource_not_found_404("The specified boat and/or load don’t exist")
    return json_response(406, error_msg='Content must be in JSON format')

@bp.route('<boat_id>', methods=['DELETE'])
def boats_delete(boat_id):
    owner = verify()
    if not owner:
        return json_response(401, error_msg='Invalid JWT')
    boat = id_validator(client, boat_id, constants.boats)
    if boat:
        key = client.key(constants.boats, int(boat_id))
        client.delete(key)
        return '', 204
    return resource_not_found_404("No boat with this boat_id exists")


@bp.route('', methods=['PUT', 'DELETE', 'PATCH'])
def boats_405():
    return json_response(405, error_msg='Edit or delete of all boats is not allowed')
