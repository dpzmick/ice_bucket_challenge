import time
from flask import Flask, jsonify
from flask import request, abort
from instagram.client import InstagramAPI
import cgi
from flask.ext.cors import cross_origin
from data_store import DataStore
from insta import handle_data
from os import environ
from threading import Thread

# get enviroment variables keys and stuff
mongo_uri = environ['INSTA_MONGO_URI']
mongo_db = environ['INSTA_MONGO_DB']
client_id = environ['INSTA_ID']
client_secret = environ['INSTA_SECRET']

storage = DataStore(mongo_uri, mongo_db)
api = InstagramAPI(client_id=client_id, client_secret=client_secret)

app = Flask(__name__, static_url_path='')

def get_new_data_and_store_it():
    if storage.get_counter() == 20:
        storage.reset_counter()
        print "Getting data"
        #data, cursor = api.tag_recent_media(None, None, 'icebucketchallenge')
        #handle_data(data, storage)
    else:
        storage.inc_counter()

@app.route("/hooks/insta", methods = ['GET'])
def get():
    print "Got a GET"
    return request.args['hub.challenge']

@app.route("/hooks/insta", methods = ['POST'])
def put():
    print "There is new data"
    # spawn a new thread because instagram wants quick response
    t = Thread(target=get_new_data_and_store_it, args=())
    t.daemon = True
    t.start()

    return jsonify( { 'accept': True } ), 201

@app.route("/json")
@cross_origin()
def get_data_as_d3_json():

    nodes = []
    indexes = {}
    links = []

    for node in storage.get_as_dictionary_iterator():

        for name in [node["name"]] + node["connections"]:
            item = {"name": name}
            if item not in nodes:
                indexes[name] = len(nodes)
                nodes.append(item)

    for node in storage.get_as_dictionary_iterator():
        n1 = node["name"]
        for connection in node["connections"]:
            n2 = connection
            links.append( {"source": indexes[n1], "target":indexes[n2] })

    return jsonify( {"nodes": nodes, "links": links} )

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
