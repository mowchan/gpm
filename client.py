import curses
from threading import Timer
from database import Database
from music import Music
from player import Player

class Client:
    def __init__(self):
        # globals
        self.artists = []
        self.albums = []
        self.tracks = {}
        self.selected_artist = None
        self.selected_album = None
        self.prompt_x = 2
        self.prompt_y = 0
        self.input_index = 0
        self.query = ''
        self.is_running = True
        self.is_showing_artists = False
        self.is_showing_albums = False
        # database, library, player
        self.init_database()
        self.init_library()
        self.init_player()
        # curses
        self.init_curses()
        self.render()

    def init_database(self):
        self.db = Database()
        self.user_device_id = self.db.get_user_device_id()

    def init_library(self):
        self.music = Music(self.user_device_id)
        # if not self.db.is_library_ready():
        # songs = self.music.get_user_songs()
        # self.db.populate_tables(songs)
        # TODO: populate_tables in a separate thread on launch if the db is already populated

    def init_player(self):
        self.player = Player()

    def init_curses(self):
        self.scr = curses.initscr()
        self.scr.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()
        self.init_colors()

    def close_curses(self):
        self.scr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        raise SystemExit

    def init_colors(self):
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def render(self):
        self.max_y, self.max_x = self.scr.getmaxyx()
        self.prompt_y = self.max_y - 2
        self.render_header()
        self.render_prompt()
        self.render_prompt_text()
        self.render_now_playing()

        while self.is_running:
            try:
                key = self.scr.getch()
                self.handle_input(key)
            except:
                self.is_running = False

        self.close_curses()

    def render_header(self):
        heading = 'gpm'
        # create window
        self.scr_header = self.scr.subwin(3, self.max_x, 0, 0)
        # draw decorations
        self.scr_header.bkgd('/', curses.color_pair(5))
        self.scr_header.hline(0, 0, '/', self.max_x, curses.color_pair(5))
        self.scr_header.hline(2, 0, '/', self.max_x, curses.color_pair(5))
        # draw heading text
        self.scr_header.addstr(1, 2, heading, curses.color_pair(6))

    def render_prompt(self):
        # create window
        self.scr_prompt = self.scr.subwin(1, self.max_x, self.prompt_y, 0)
    
    def render_prompt_text(self):
        # clear prompt window, draw text, refresh window
        self.scr_prompt.clear()
        self.scr_prompt.addstr(0, 0, '$', curses.color_pair(0))
        self.scr_prompt.addstr(0, self.prompt_x, 'artist', curses.color_pair(7))
        self.scr_prompt.refresh()
        # set cursor position
        self.scr.move(self.prompt_y, self.prompt_x)

    def render_input_start(self):
        self.scr_prompt.clear()
        self.scr_prompt.addstr(0, 0, '$', curses.color_pair(0))
        self.scr_prompt.refresh()

    def render_now_playing(self):
        # create window
        self.scr_np = self.scr.subwin(4, self.max_x - 2, 4, 2)

    def render_now_playing_text(self):
        track = self.player.album['tracks'][str(self.player.track_number)]
        self.clear_now_playing()
        self.scr_np.addstr(0, 0, track['name'], curses.color_pair(2) + curses.A_BOLD)
        self.scr_np.addstr(1, 0, self.selected_artist['name'], curses.color_pair(2) + curses.A_DIM)
        self.scr_np.addstr(2, 0, self.selected_album['name'], curses.color_pair(2) + curses.A_DIM)
        self.scr_np.refresh()
        # set cursor position
        self.scr.move(self.prompt_y + 1, self.prompt_x)
        self.scr.refresh()

    def clear_now_playing(self):
        self.scr_np.clear()
        self.scr_np.refresh()
        self.scr.move(self.prompt_y + 1, self.prompt_x)

    def render_artists(self, artists):
        self.artists = artists
        self.list_cur_y = 0
        self.scr_list = self.scr.subwin(self.max_y - 8, self.max_x - 2, 4, 2)
        for index, artist in enumerate(self.artists):
            self.scr_list.addstr(index, 0, artist['name'], curses.color_pair(2))
        self.scr.move(4, 2)
        self.is_showing_artists = True
        self.highlight_selected_list_item()

    def get_active_list(self):
        if self.is_showing_albums:
            return self.albums
        if self.is_showing_artists:
            return self.artists

    def highlight_selected_list_item(self):
        active_list = self.get_active_list()
        self.scr_list.chgat(self.list_cur_y, 0, len(active_list[self.list_cur_y]['name']), curses.A_REVERSE)
        self.scr_list.refresh()

    def increment_selected_list_item(self):
        active_list = self.get_active_list()
        cur_y, cur_x = self.scr.getyx()
        self.scr.move(cur_y + 1, cur_x)
        self.scr_list.chgat(self.list_cur_y, 0, len(active_list[self.list_cur_y]['name']), curses.color_pair(2))
        self.list_cur_y += 1
        self.highlight_selected_list_item()

    def decrement_selected_list_item(self):
        active_list = self.get_active_list()
        cur_y, cur_x = self.scr.getyx()
        self.scr.move(cur_y - 1, cur_x)
        self.scr_list.chgat(self.list_cur_y, 0, len(active_list[self.list_cur_y]['name']), curses.color_pair(2))
        self.list_cur_y -= 1
        self.highlight_selected_list_item()

    def select_list_item(self):
        if self.is_showing_albums:
            self.selected_album = self.albums[self.list_cur_y]
            self.scr_list.clear()
            self.is_showing_artists = False
            self.is_showing_albums = False
            self.play_album()
            self.render_now_playing()
        elif self.is_showing_artists:
            self.selected_artist = self.artists[self.list_cur_y]
            self.albums = self.selected_artist['albums']
            self.scr_list.clear()
            for index, album in enumerate(self.albums):
                # TODO: scrolling
                if (index < self.max_y - 8):
                    self.scr_list.addstr(index, 0, album['name'], curses.color_pair(2))
            self.scr.move(4, 2)
            self.list_cur_y = 0
            self.scr_list.refresh()
            self.is_showing_albums = True
            self.highlight_selected_list_item()

    def handle_input(self, key):
        # self.player is loaded with URL; playing or paused
        if self.is_showing_albums or self.is_showing_artists:
            if key == curses.KEY_DOWN:
                self.increment_selected_list_item()
            elif key == curses.KEY_UP:
                self.decrement_selected_list_item()
            elif key == 10: # enter
                self.select_list_item()
        else:
            if not self.player is None and self.player.is_loaded: # player is loaded with url, playing or paused
                if key == curses.KEY_DOWN:
                    self.pause_song()
                elif key == curses.KEY_RIGHT:
                    self.play_next_song()
                elif key == curses.KEY_LEFT:
                    self.play_prev_song()
                elif key == 27: # escape
                    self.clear_playback_timer()
                    self.clear_now_playing()
                    self.player.reset()
            # no playback keys pressed; continue normal input handling
            if key == 27:
                self.is_running = False
            # backspace, mac "delete" key
            if key == curses.KEY_BACKSPACE or key == 127:
                # the query is about to be cleared
                if self.input_index < 2:
                    self.handle_input_clear()
                else:
                    self.handle_input_backspace()
            elif key == 10: # enter
                self.handle_input_enter()
            elif not key == curses.KEY_DOWN and not key == curses.KEY_UP and not key == curses.KEY_LEFT and not key == curses.KEY_RIGHT and not key == 27:
                if self.input_index == 0:
                    self.render_input_start()
                self.handle_input_concat(key)

    def handle_input_clear(self):
        self.query = ''
        self.input_index = 0
        self.render_prompt_text()

    def handle_input_backspace(self):
        self.input_index = self.input_index - 1
        self.query = self.query[0 : len(self.query) - 1]
        # replace previous character with a space character
        self.scr_prompt.addstr(0, self.prompt_x + self.input_index, ' ', curses.color_pair(2))
        self.scr_prompt.refresh()
        # set cursor position to previous position
        self.scr.move(self.prompt_y, self.prompt_x + self.input_index)

    def handle_input_enter(self):
        results = self.db.search_artists(self.query)
        if len(results) > 0:
            self.clear_now_playing()
            self.handle_input_clear()
            self.render_artists(results)

    def handle_input_concat(self, key):
        character = chr(key)
        self.query += character
        self.scr_prompt.addstr(0, self.prompt_x + self.input_index, character, curses.color_pair(2))
        self.scr_prompt.refresh()
        self.input_index += 1

    def play_album(self):
        self.player.reset()
        self.player.set_album(self.selected_album)
        self.play_song()

    def play_song(self):
        try:
            track = self.player.album['tracks'][str(self.player.track_number)]
            track_duration = track['duration']
            track_url = self.music.get_song_stream_url(track['stream_id'])
            self.player.load_url(track_url)
            self.player.play()
            self.player.playback_timer = Timer(track_duration, self.play_next_song)
            self.player.playback_timer.start()
            self.render_now_playing_text()
        except:
            self.clear_now_playing()

    def play_next_song(self):
        if (self.player.track_number < len(self.player.album)):
            self.clear_playback_timer()
            self.player.increment_track_number()
            self.play_song()

    def play_prev_song(self):
        if (self.player.track_number > 1):
            self.clear_playback_timer()
            self.player.decrement_track_number()
            self.play_song()

    def pause_song(self):
        # TODO: pause thread when player is paused...
        # if not self.player.playback_timer is None:
        #     if self.player.is_playing:
        #         self.player.playback_timer.pause()
        #     else:
        #         self.player.playback_timer.start()
        self.player.pause()

    def clear_playback_timer(self):
        if self.player.playback_timer.is_alive():
                self.player.playback_timer.cancel()

Client()