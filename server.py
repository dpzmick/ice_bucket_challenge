from pymongo import MongoClient
import time
from flask import Flask, jsonify
from flask import request, abort
from instagram.client import InstagramAPI
import cgi
from flask.ext.cors import cross_origin
from data_store import DataStore
from insta import handle_data
from os import environ

# get enviroment variables keys and stuff
mongo_uri = environ['INSTA_MONGO_URI']
mongo_db = environ['INSTA_MONGO_DB']
client_id = environ['INSTA_ID']
client_secret = environ['INSTA_SECRET']

app = Flask(__name__, static_url_path='')

storage = DataStore(mongo_uri, mongo_db)
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
