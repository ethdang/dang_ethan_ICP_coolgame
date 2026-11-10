import pygame as pg

######### game #########
FPS = 120
PHYSICS_UPDATE_RATE = 60

######### visuals #########
TILESIZE = 32

######### color #########
BG_COLOR = (138, 205, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (141, 141, 141)
RED = (255,0,0)
LIGHT_GREEN = (49, 148, 55)
GREEN = (0,255,0)
BLUE = (0,0,255)
GOAL_BLUE = (0,255,255)

######### player settings #########
PLAYER_SPEED = 2.5
PLAYER_JUMP = 5.5
PLAYER_HIT_RECT = pg.Rect(0,0, TILESIZE - 14, TILESIZE - 5)
PLAYER_FRIC = 0.05
GRAVITY = 9.8

######### mob settings #########
MOB_SPEED = 150
MOB_HIT_RECT = pg.Rect(0,0, TILESIZE - 10, TILESIZE - 10)
######### screen window #########
SCREEN_WIDTH = 1024 # width of screen
SCREEN_HEIGHT = 768 # height of screen

TITLE = "average chicken horse"