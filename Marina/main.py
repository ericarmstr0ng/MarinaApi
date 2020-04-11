from google.cloud import datastore
from flask import Flask, request, abort, jsonify, Blueprint, render_template
import json
import constants
from jsonschema import validate
import os
import boats, loads, auth


app = Flask(__name__)
app.register_blueprint(boats.bp)
app.register_blueprint(loads.bp)
app.register_blueprint(auth.bp)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
client = datastore.Client()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/IngloriousLoki/Desktop/Cloud/Marina/project-loki-0c4fe8ce166f.json"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
