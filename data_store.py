from pymongo import MongoClient

# stores data in mongo and presents a fairly nice interface to access the data
# does not store any data in memory, everything is a database request
# assumes all usernames are unique
class DataStore:
    def __init__(self, monogo_uri, monogo_db_name):
        # connect to mongo
        self.client = MongoClient(monogo_uri)
        self.db = self.client[monogo_db_name]

    def get_connections_for(self, username):
        found = self.db.nodes.find( {"name" : username} )
        return found["connections"]

    def connect(self, user1, user2):
        self.db.nodes.update(
                { "name" : user1 },
                {
                    "$addToSet" : { "connections" : user2 }
                },
                upsert=True
            )

    def get_as_dictionary_iterator(self):
        return self.db.nodes.find()

if __name__ == "__main__":
    d = DataStore("test2")
    d.connect("David", "Scott")
    d.connect("Scott", "Lawrence")
    d.connect("David", "Lawrence")
    for e in d.get_as_dictionary_iterator():
        print e
