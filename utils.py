import pygame as pg
from settings import *
from math import *

class Map:
    def __init__(self, filename):
        self.data = []

        # open up a file name as f
        with open(filename, "rt") as f: 
            for line in f:
                # copy each line of the file into our own list
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0]) # length of first line
        self.tileheight = len(self.data) # length of list

        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE