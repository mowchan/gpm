import vlc

class Player:
    def __init__(self):
        self.instance = vlc.Instance('--verbose=-1')
        self.player = self.instance.media_player_new()
        self.reset()

    def set_album(self, album):
        self.album = album

    def set_track_number(self, track_number):
        self.track_number = track_number

    def increment_track_number(self):
        self.track_number += 1
    
    def decrement_track_number(self):
        self.track_number -= 1

    def load_url(self, url):
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.is_loaded = True

    def play(self):
        self.is_playing = True
        self.player.play()

    def pause(self):
        self.is_playing = not self.is_playing
        self.player.pause()

    def reset(self):
        self.player.stop()
        self.is_loaded = False
        self.is_playing = False
        self.track_number = 1
        self.album = None
        self.song = None