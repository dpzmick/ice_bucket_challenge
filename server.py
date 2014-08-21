from flask import Flask, jsonify
from flask import request
app = Flask(__name__)

@app.route("/hooks/insta", methods = ['GET'])
def get():
    return jsonify( { "label": "I'm here!" } )

@app.route("/hooks/insta", methods = ['POST'])
def put():
    if not request.json or not 'title' in request.json:
            abort(400)
    return jsonify( { 'task': request.json } ), 201

if __name__ == "__main__":
    app.run(debug=True)
