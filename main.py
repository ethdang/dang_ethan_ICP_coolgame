# this file was created by Ethan Dang
# code inspired by Chris Bradfield who was inspired by Notch

# import pygame because we are making a game; use pg so it's easier to access
import pygame as pg
from os import path
# import sprites so we can access our sprites
from sprites import *
# import settings so we can access our settings and use MODULARITY
from settings import *
from utils import *



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

'''

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

    def load_data(self, map):
        self.game_dir = path.dirname(__file__)
        self.image_dir = path.join(self.game_dir, '_images')
        self.sound_dir = path.join(self.game_dir, '_audio')
    
        self.map = Map(path.join(self.game_dir, map))

    def new(self): # when we create or start up a new game
        self.load_data("level1.txt")
        self.all_sprites = pg.sprite.Group() # group all sprites
        self.all_walls = pg.sprite.Group() # group all walls
        self.all_mobs = pg.sprite.Group() # group all mob

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == "0": # wall
                    Wall(self, col, row)
                if tile == "e": # mob spawn
                    Mob(self, col, row, RED)
                if tile == "b":
                    Mob(self, col, row, BLUE)
        # instantiate after the walls to appear ABOVE the walls
        for row, tiles in enumerate (self.map.data):
            for col, tile in enumerate(tiles):
                if tile == "P": # player spawn
                    self.player = Player(self, col, row) # instantiate the player


    def run(self): # main game loop
        self.playing = True

        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: # input: player QUITs the game
                if self.playing:
                    self.playing = False # output: game is no longer playign

                self.running = False # output: game is no longer running

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill(BG_COLOR) # use background color

        self.all_sprites.draw(self.screen) # draw all sprites
        pg.display.flip()

if __name__ == "__main__": # only run if this is the main file
    g = Game()

while g.running:
    g.new()
    g.run()