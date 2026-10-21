# this file was created by Ethan Dang
# code inspired by Chris Bradfield who was inspired by Notch

# import pygame because we are making a game; use pg so it's easier to access
import pygame as pg
from os import path
# import sprites so we can access our sprites
from sprites import *
# import settings so we can access our settings and use MODULARITY
from settings import *
from playerResource import *
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

    CLASH ROYALE

        GOALS:
            destroy the opponent's towers
            become the best
        
        RULES:
            you can only place on your side
            you have a limited amount of elixer

        FEEDBACK:
            place a card and it appears on screen
            elixer bar
            tower health

        FREEDOM:
            you can build your deck however you want
            place any card in your deck
            choose your own strategy

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


        self.high_score = 0
        self.score = 0

    def load_data(self, map):
        self.game_dir = path.dirname(__file__)
        self.image_dir = path.join(self.game_dir, '_images')

        # sound handling
        self.sound_dir = path.join(self.game_dir, '_audio')
        self.coin_collect = pg.mixer.Sound(path.join(self.sound_dir, "coin_collect.wav"))
        self.map = Map(path.join(self.game_dir, map))

        self.game_save_file = path.join(self.game_dir, "highscore.txt")

        try:
            with open(self.game_save_file, 'x', encoding = "utf-8") as file:
                file.write("new file")
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
        self.load_data("_images/level_sprite_sheet.png")
        self.all_sprites = pg.sprite.Group() # group all sprites
        self.all_walls = pg.sprite.Group() # group all walls
        self.all_mobs = pg.sprite.Group() # group all mob
        self.all_collectables = pg.sprite.Group() # group all collectable

        # self.camera = Camera(self, 0,0, WHITE)

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == "0": # wall
                    Wall(self, col, row)
                if tile == "E": # mob spawn
                    Mob(self, col, row)
                if tile == "C":
                    Collectable(self, col, row, BLUE, 'coin', 1)
        # instantiate after the walls to appear ABOVE the walls
        for row, tiles in enumerate (self.map.data):
            for col, tile in enumerate(tiles):
                if tile == "P": # player spawn
                    self.player = Player(self, col, row) # instantiate the player

        # self.camera = self.player

        pg.mixer.music.load(path.join(self.sound_dir, "background_music.mp3"))
        pg.mixer.music.play(loops=-1)


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
                if (self.score > self.high_score):
                    with open(path.join(self.game_dir, self.game_save_file), 'w') as file:
                        file.write(str(self.score))
                        
                if self.playing:
                    self.playing = False # output: game is no longer playign

                self.running = False # output: game is no longer running
               

    def draw_text(self, text, size, color, x, y):
        font_name = pg.font.match_font('ariel')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect =  text_surface.get_rect()
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)

    def update(self):
        self.all_sprites.update()

    def draw(self): # higher up draws first
        self.screen.fill(BG_COLOR) # use background color

        self.all_sprites.draw(self.screen) # draw all sprites

        self.draw_text("Framex per second: " + str(floor(1/self.dt)), 24, WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.draw_text("moneys: " + str(COLLECTED["coin"]), 24, WHITE, SCREEN_WIDTH/12, SCREEN_HEIGHT/8)
        self.draw_text("score: " + str(self.score), 24, WHITE, SCREEN_WIDTH/12, SCREEN_HEIGHT/10)
        self.draw_text("high score: " + str(self.high_score), 24, WHITE, SCREEN_WIDTH/12, SCREEN_HEIGHT/12)
        pg.display.flip()

if __name__ == "__main__": # only run if this is the main file
    g = Game()

while g.running:
    g.new()
    g.run()