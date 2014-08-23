from pymongo import MongoClient
import time
from flask import Flask, jsonify
from flask import request, abort
from instagram.client import InstagramAPI
import cgi
from flask.ext.cors import cross_origin
from data_store import DataStore
from insta import handle_data
from private import client_id, client_secret, mongo_uri

app = Flask(__name__, static_url_path='')

storage = DataStore(mongo_uri, "instagram_data")
api = InstagramAPI(client_id=client_id, client_secret=client_secret)

def get_new_data_and_store_it():
    data, cursor = api.tag_recent_media(None, None, 'icebucketchallenge')
    handle_data(data, storage)
    time.sleep(2)

@app.route("/hooks/insta", methods = ['GET'])
def get():
    print "Got a GET"
    return request.args['hub.challenge']

@app.route("/hooks/insta", methods = ['POST'])
def put():
    if not request.json:
        abort(400)

    print "Got new data"
    get_new_data_and_store_it()
    return jsonify( { 'accept': True } ), 201

@app.route("/json")
@cross_origin()
def get_data_as_d3_json():
    return "not yet implemented"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
