import pygame as pg
from settings import *
from math import *

class Map:
    def __init__(self, filename):
        self.data = []
        self.levelspritesheet = pg.image.load(filename).convert()

        for y in range(self.levelspritesheet.height):
            cur_line = "" # reset current line

            for x in range(self.levelspritesheet.width):
                found_color = self.levelspritesheet.get_at((x,y))
                if found_color == WHITE: # wall
                    cur_line += "0"
                elif found_color == BLACK: # nothing
                    cur_line += "C"
                elif found_color == GREEN: # player
                    cur_line += "P"
                elif found_color == RED: # enemy
                    cur_line += "E"

            self.data.append(cur_line) # add our line STRING into our map LIST

            self.tilewidth = len(self.data[0]) # length of first line
            self.tileheight = len(self.data) # length of list

            self.width = self.tilewidth * TILESIZE
            self.height = self.tileheight * TILESIZE

class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height): # get the image from position in sprite sheet given its size and pos
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0,0), (x,y, width, height))
        new_image = pg.transform.scale(image, (width, height))
        image = new_image
        image.set_colorkey(BLACK)
        return image

class Cooldown:
    def __init__(self, time):
        self.start_time = 0
        self.time = time
        self.current_time = self.time

    def ticking(self):
        # update current time 
        self.current_time = floor((pg.time.get_ticks())/1000)
        self.delta = self.current_time = self.event_time

    def start(self):
        # update start time
        self.start_time = pg.time.get_ticks()

    def ready(self):
        self.current_time = pg.time.get_ticks()

        # return true or false depending on whether the cooldown is over
        if self.current_time - self.start_time >= self.time:
            return True
    
        return False