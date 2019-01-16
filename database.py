import os
import sqlite3 as lite

class Database:
    def __init__(self):
        db_path = os.path.expanduser('~') + '/.gpm/'
        db_file = 'gpm.db'
        self.con = lite.connect(db_path + db_file)
        self.db = self.con.cursor()
        self.init_tables()
    
    def init_tables(self):
        # create tables
        self.db.execute('CREATE TABLE IF NOT EXISTS user(device_id TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS artists(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS albums(id INTEGER PRIMARY KEY AUTOINCREMENT, artist_id INT, name TEXT)')
        # TODO: support multiple artists on an album
        self.db.execute('CREATE TABLE IF NOT EXISTS tracks(id INTEGER PRIMARY KEY AUTOINCREMENT, album_id INT, name TEXT, stream_id TEXT, disc_number INT, track_number INT, duration INT)')
        # self.db.execute('INSERT INTO user VALUES("DEVICE_ID")')
        # self.con.commit()
 
    def get_user_device_id(self):
        self.db.execute('SELECT device_id FROM user')
        return self.db.fetchone()[0]

    def populate_tables(self, songs):
        for song in songs:
            artist_name = song['artist']
            album_name = song['album']
            disc_number = song['discNumber']
            duration = int(song['durationMillis']) / 1000
            track_name = song['title']
            track_number = song['trackNumber']
            track_stream_id = song['id']
            artist_id = self.insert_artist(artist_name)
            album_id = self.insert_album(album_name, artist_id)
            track_id = self.insert_track(track_name, track_stream_id, disc_number, track_number, album_id, duration)
        self.con.commit()

    def insert_artist(self, artist_name):
        self.db.execute('SELECT id FROM artists WHERE name=?', (artist_name,))
        artist = self.db.fetchone()

        if artist is None:
            # artist does not exist yet, insert it
            self.db.execute('INSERT INTO artists VALUES(NULL, ?)', (artist_name,))
            # return id of the inserted row
            return self.db.lastrowid
        else:
            # artist exists, return id
            return artist[0]

    def insert_album(self, album_name, artist_id):
        self.db.execute('SELECT id FROM albums WHERE name=? AND artist_id=?', (album_name, artist_id))
        album = self.db.fetchone()

        if album is None:
            # album does not exist yet, insert it
            self.db.execute('INSERT INTO albums VALUES(NULL, ?, ?)', (artist_id, album_name))
            # return id of the inserted row
            return self.db.lastrowid
        else:
            # album exists, return id
            return album[0]

    def insert_track(self, track_name, track_stream_id, disc_number, track_number, album_id, duration):
        self.db.execute('SELECT id FROM tracks WHERE name=? AND disc_number=? AND track_number=? AND album_id=?', (track_name, disc_number, track_name, album_id))
        track = self.db.fetchone()

        if track is None:
            # track does not exist yet, insert it
            self.db.execute('INSERT INTO tracks VALUES(NULL, ?, ?, ?, ?, ?, ?)', (album_id, track_name, track_stream_id, disc_number, track_number, duration))
            # return id of the inserted row
            return self.db.lastrowid
        else:
            # track exists, return id
            return track[0]

    def search_artists(self, query_string):
        self.db.execute('SELECT * FROM artists WHERE name LIKE ?', ('%' + query_string + '%',))
        artists = self.db.fetchall()
        artists_normalized = []

        for artist in artists:
            artist_normalized = {
                'id': artist[0],
                'name': artist[1],
                'albums': []
            }
            self.db.execute('SELECT * FROM albums WHERE artist_id=?', (artist_normalized['id'],))
            albums = self.db.fetchall()

            for album in albums:
                album_normalized = {
                    'id': album[0],
                    'name': album[2]
                }
                self.db.execute('SELECT * FROM tracks WHERE album_id=?', (album[0],))
                tracks = self.db.fetchall()
                tracks_normalized = {}

                for track in tracks:
                    track_number = track[5]
                    tracks_normalized[str(track_number)] = {
                        'name': track[2],
                        'stream_id': track[3],
                        'disc_number': track[4],
                        'duration': track[6],
                        'track_number': track_number
                    }

                album_normalized['tracks'] = tracks_normalized
                artist_normalized['albums'].append(album_normalized)

            artists_normalized.append(artist_normalized)

        return artists_normalized

Database()