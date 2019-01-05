import os
from tinydb import TinyDB, Query

class Database:
    def __init__(self):
        self.json_dir = os.path.expanduser('~') + '/.gpm/'
        self.json_name = 'gpm.json'
        self.create_json()
        self.db = TinyDB(self.json_dir + self.json_name, default_table='gpm')
        self.user = Query()

    def create_json(self):
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)
            open(self.json_dir + self.json_name, 'w+')

    def set_user_device_id(self, user_device_id):
        if self.db.contains(self.user.device_id):
            # TODO: overwrite device_id
            print('todo... already exists')
        else:
            self.db.insert({'device_id': user_device_id})

    def get_user_device_id(self):
        if self.db.contains(self.user.device_id):
            return self.db.get(self.user.device_id)['device_id']
        else:
            # TODO: handle no device_id with exception?
            print('no device_id')

    def is_library_ready(self):
        return self.db.contains(self.user.library)

    def build_library(self, songs):
        library = {}

        for song in songs:
            artist = song['artist']
            album = song['album']
            trackNumber = song['trackNumber']

            if artist in library:
                # artist exists in db...
                if album in library[artist]:
                    # album exists for artist in db, add song
                    library[artist][album][trackNumber] = song
                else:
                    # create album for artist, add song
                    library[artist][album] = {}
                    library[artist][album][trackNumber] = song
            else:
                # create artist, create album for artist, add song
                library[artist] = {}
                library[artist][album] = {}
                library[artist][album][trackNumber] = song

        self.db.insert({ 'library': library })

    def get_album(self, artist, album):
        library = self.db.get(self.user.library)['library']
        return library[artist][album]