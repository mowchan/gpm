from gmusicapi import Mobileclient

class Music:
    def __init__(self, user_device_id):
        self.api = Mobileclient()
        self.authenticate(user_device_id)
    
    def authenticate(self, user_device_id):
        # TODO: the rest of the auth process for new users
        self.api.oauth_login(device_id = user_device_id)
    
    def get_user_songs(self):
        return self.api.get_all_songs()

    def get_song_stream_url(self, song_id):
        return self.api.get_stream_url(song_id)