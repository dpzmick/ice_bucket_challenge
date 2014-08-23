from pymongo import MongoClient

# stores data in mongo and presents a fairly nice interface to access the data
# does not store any data in memory, everything is a database request
# assumes all usernames are unique
class DataStore:
    def __init__(self, monogo_uri, monogo_db_name):
        # connect to mongo
        self.client = MongoClient(monogo_uri)
        self.db = self.client[monogo_db_name]

        # init the counter
        self.reset_counter()

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

    # also implements a hacky counter thing
    def get_counter(self):
        return self.db.counter.find()[0]["count"]
    
    def inc_counter(self):
        self.db.counter.update({ "name" : "counter" }, { "$inc" : { "count" : 1 }})

    def reset_counter(self):
        self.db.counter.drop()
        self.db.counter.insert( { "name" : "counter", "count": 0 } )




if __name__ == "__main__":
    d = DataStore("mongodb://localhost:27017", "test2")
    d.connect("David", "Scott")
    d.connect("Scott", "Lawrence")
    d.connect("David", "Lawrence")
    for e in d.get_as_dictionary_iterator():
        print e

    print d.get_counter()
    d.inc_counter()
    print d.get_counter()

    d.reset_counter()

    print d.get_counter()
    d.inc_counter()
    print d.get_counter()

