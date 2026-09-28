import pygame as pg

######### game #########
FPS = 120

######### visuals #########
TILESIZE = 32

######### color #########
BG_COLOR = (138, 205, 255)
WHITE = (255, 255, 255)
RED = (255,0,0)
GREEN = (49, 148, 55)
BLUE = (0,0,255)

######### player settings #########
PLAYER_SPEED = 200
PLAYER_HIT_RECT = pg.Rect(0,0, TILESIZE - 5, TILESIZE - 5)
GRAVITY = 400

######### mob settings #########
MOB_SPEED = 150

######### screen window #########
SCREEN_WIDTH = 1024 # width of screen
SCREEN_HEIGHT = 768 # height of screen

TITLE = "COOLer game"