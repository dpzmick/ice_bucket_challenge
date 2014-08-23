# how to handle raw data
def handle_data(data, storage):
    for post in data:
        uname = '@' + str(post.user.username)
        for reference in [word for word in post.caption.text.split(" ") if word.startswith("@")]:
            storage.connect(uname, reference)

if __name__ == "__main__":
    from instagram.client import InstagramAPI
    import cgi
    import time
    from data_store import DataStore
    from private import client_id, client_secret, mongo_uri

    storage = DataStore(mongo_uri, "instagram_data")

    # connect to instagram API
    api = InstagramAPI(client_id=client_id, client_secret=client_secret)

    # get data already on instagram
    data, cursor = api.tag_recent_media(None, None, 'icebucketchallenge')
    max_id = -1
    while data != None:
        handle_data(data, storage)
        time.sleep(2)
        if max_id == cgi.parse_qsl(cursor)[1][1]:
            break
            # we have it all
        else:
            max_id = cgi.parse_qsl(cursor)[1][1]
            data, cursor = api.tag_recent_media(None, max_id, 'icebucketchallenge')

    # create a subscription for new data
    api.create_subscription(object='tag', object_id='icebucketchallenge', aspect='media',
            callback_url='http://98.201.226.93:5000/hooks/insta')
