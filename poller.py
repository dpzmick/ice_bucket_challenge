import time
from flask import Flask, jsonify
from flask import request, abort
from instagram.client import InstagramAPI
import cgi
from flask.ext.cors import cross_origin
from data_store import DataStore
from insta import handle_data
from os import environ
from threading import Thread, Lock

# get enviroment variables keys and stuff
mongo_uri = environ['INSTA_MONGO_URI']
mongo_db = environ['INSTA_MONGO_DB']
client_id = environ['INSTA_ID']
client_secret = environ['INSTA_SECRET']

storage = DataStore(mongo_uri, mongo_db)
api = InstagramAPI(client_id=client_id, client_secret=client_secret)

collection_lock = Lock()
app = Flask(__name__)

def get_new_data_and_store_it():
    while True:
        print "Getting data"
        data, cursor = api.tag_recent_media(None, None, 'icebucketchallenge')
        time.sleep(2)

        max_id = -1
        while data != None:

            collection_lock.acquire()
            handle_data(data, storage)
            collection_lock.release()

            if max_id == cgi.parse_qsl(cursor)[1][1]:
                # we have everything we can get now
                break

            else:
                max_id = cgi.parse_qsl(cursor)[1][1]
                print "Getting data"
                data, cursor = api.tag_recent_media(None, max_id, 'icebucketchallenge')
                time.sleep(2)

@app.route("/json")
@cross_origin()
def get_data_as_d3_json():
    collection_lock.acquire()

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

    collection_lock.release()
    return jsonify( {"nodes": nodes, "links": links} )

if __name__ == "__main__":
    t = Thread(target=get_new_data_and_store_it, args=())
    t.start()
    app.run(host='0.0.0.0')
    t.join()
