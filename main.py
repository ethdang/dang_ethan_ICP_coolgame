# this file was created by Ethan Dang
# code inspired by Chris Bradfield who was inspired by Notch
# multiplayer code from TechWithTime https://www.techwithtim.net/tutorials/python-online-game-tutorial

# import pygame because we are making a game; use pg so it's easier to access
import pygame as pg
from os import path
# import sprites so we can access our sprites
from sprites import *
# import settings so we can access our settings and use MODULARITY
from settings import *
from playerResource import *
from utils import *
from network import Network


'''
    to start playing
    1. run server.py
    2. in a seperate terminal, run main py
'''



'''
    Data Types: 
        boolean, JSON, string, 
        integer, float, doubles

    Input (events): 
        keyboard, mouse, touch screen, 
        camera, motion, location, time?, power button,
        computer settings, micropphone, etc

    Process:
        cursor position, position of player, score,
        enemy position, velocity, aim in FPS, etc

    Output:
        graphics - things are drawn, sound - jump,
        haptics - vibration, etc

    Ultimate CHicken Horse Ripoff

        GOALS:
            be the last one standing
            be the best
        
        RULES:
            no player to player collision
            set pool of objects you can place

        FEEDBACK:
            lava
            particles
            score

        FREEDOM:
            you can build the map however you want
            beat the platform however you want
            choose your own strategy

'''


clientNumber = 0

class Game: 
    def __init__(self):
        pg.init() # game engine
        pg.mixer.init() # sound

        # initialize the screen
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        print("game initialized")

        # set window title
        pg.display.set_caption(TITLE) 

        self.running = True # game is running
        self.playing = True # game is playing

        self.clock = pg.time.Clock() # add clock
        self.start_time = 0
        self.current_time = 0

        self.high_score = 0 # store high score
        self.score = 0 # score current score

        self.player_spawn = 0 # store spawn point

        try: # try to connect to network
            self.network = Network()
        except OSError as error: # if we cannot connect
            print("Could not connect to server:", error)
            self.network = None

    def load_data(self, map):
        self.game_dir = path.dirname(__file__)
        self.image_dir = path.join(self.game_dir, '_images')

        # sound handling
        self.sound_dir = path.join(self.game_dir, '_audio')
        self.coin_collect = pg.mixer.Sound(path.join(self.sound_dir, "coin_collect.wav"))
        self.map = Map(path.join(self.game_dir, map))

        self.game_save_file = path.join(self.game_dir, "highscore.txt")

        try: # try excpetion blocks help us debug
            with open(self.game_save_file, 'x', encoding = "utf-8") as file:
                file.write("new file") # no file exists? create a new file
            print("file created")
        except FileExistsError:
            print("file already exists")

        with open(self.game_save_file, 'r') as file:
            try:
                self.high_score = int(file.read())
            except:
                self.high_score = 0 # set highscore to 0 if not found
                print("high score set to 0")

    def new(self): # when we create or start up a new game
        self.load_data("_images/maps_v3.png")
        self.all_sprites = pg.sprite.Group() # group all sprites
        self.all_mobs = pg.sprite.Group() # group all mob
        
        self.all_collectables = pg.sprite.Group() # group all collectable
        self.all_particles = pg.sprite.Group() # group all particles
        
        self.all_walls = pg.sprite.Group() # group all walls
        self.all_no_touch = pg.sprite.Group() # group all non collidables
        self.all_kill_tile = pg.sprite.Group() # group all particles
        self.all_win_tile = pg.sprite.Group() # group all particles

        self.all_mouse_tile = pg.sprite.Group() # group all mouse tile
        # self.camera = Camera(self, 0,0, WHITE)

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                pos = vec(col, row)

                if tile == "0": # wall
                    Wall(self, pos, "grass.png")
                elif tile == "O": # non-collidable wall
                    NoTouchWall(self, pos, "dirt.png")
                elif tile == "K": # kill tile
                    KillTile(self, pos)
                elif tile == "W": # win/goal tile
                    WinTile(self, pos, "dirt.png")
                elif tile == "C":
                    pass
                    # Collectable(self, col, row, BLUE, 'coin', 1)
                
        # instantiate after the walls to appear ABOVE the walls
        for row, tiles in enumerate (self.map.data):
            for col, tile in enumerate(tiles):
                pos = vec(col, row)

                if tile == "P": # player spawn
                    self.player = Player(self, pos) # instantiate the player
                    self.player_spawn = vec(pos) # set player spawn for respawns

        MouseTile(self)

        # self.camera = self.player

        pg.mixer.music.load(path.join(self.sound_dir, "background_music.mp3"))
        pg.mixer.music.play(loops=-1)

    def read_pos(str):
        str = str.split(",")
        return int(str[0]), int(str[1])


    def make_pos(tup):
        return str(tup[0]) + "," + str(tup[1])


    def run(self):
            self.playing = True
            # each physic step represents 1/upd rate of a second
            physics_step = 1 / PHYSICS_UPDATE_RATE
            # elapsed time in which physics has not been updated yet
            accumulator = 0

            self.start_time = pg.time.get_ticks()

            while self.playing:
                # limits rendering speed and returns milliseconds since prev frame
                frame_time = self.clock.tick(FPS) / 1000
                # time gets added to accumulator, capped at .25 sec
                # to prevent long pause from triggering alot of physics updates
                accumulator += min(frame_time, 0.25)

                self.events()

                # while there is enough time for a physics step
                while accumulator >= physics_step:
                    self.current_time = round((pg.time.get_ticks() - self.start_time)/1000, 2)
                    self.dt = physics_step # set dt to 1/120
                    self.update() # upd movement and collisions
                    accumulator -= physics_step # subtract time it takes to process

                self.draw()


    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: # input: player QUITs the game
                if (self.score > self.high_score):
                    with open(path.join(self.game_dir, self.game_save_file), 'w') as file:
                        file.write(str(self.score))
                if (self.network): # send player score to network
                    response = self.network.send("score:" + str(self.score))
                    print("Server response:", response)

                if self.playing:
                    self.playing = False # output: game is no longer playign

                self.running = False # output: game is no longer running
               

    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('ariel') # get font
        font = pg.font.Font(font_name, size) # set font
        text_surface = font.render(text, True, color)
        text_rect =  text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)

    def update(self):
        self.all_sprites.update()

    def draw(self): # higher up draws first
        self.screen.fill(BG_COLOR) # use background color

        self.all_sprites.draw(self.screen) # draw all sprites

        self.draw_text("Framex per second: " + str(self.clock.get_fps()), 24, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT - 50)
        self.draw_text("score: " + str(self.score), 24, WHITE, SCREEN_WIDTH/12, SCREEN_HEIGHT/10)
        self.draw_text("high score: " + str(self.high_score), 24, WHITE, SCREEN_WIDTH/12, SCREEN_HEIGHT/12)
        self.draw_text("current time: " + str(self.current_time), 24, WHITE, SCREEN_WIDTH/2, 100)
        pg.display.flip()

if __name__ == "__main__": # only run if this is the main file
    g = Game()

while g.running:
    g.new()
    g.run()