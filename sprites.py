import pygame as pg
from settings import *
from pygame.sprite import Sprite # import sprite
from utils import *

from os import path # import path from our operating system

vec = pg.math.Vector2

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
    if dir == 'x': # checking for x collision
        # me, wall, destroy, return if we actually collided
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)

        if hits:
            # if we are colliding from the right
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                # reposition sprite to the left side of the wall
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2

            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x

    if dir == 'y-floor':
        sprite.hit_rect.centery += 1
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect) 

        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                # sprite.vel.y = 0
                sprite.touching_ground = True

            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
        
        elif sprite.touching_ground:
            sprite.touching_ground = False

        sprite.hit_rect.centery -= 1

    if dir == 'y-ciel':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect) 

        if hits:
            if hits[0].rect.centery < sprite.hit_rect.centery: # ceiling
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2

            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Player(Sprite):
    def __init__(self, game, x, y):
        # put it in the all sprites group immediately
        self.groups = game.all_sprites

        Sprite.__init__(self, self.groups) # initialize sprite

        self.game = game # allow the player to access game

        self.spritesheet = Spritesheet(path.join(self.game.image_dir, "sprite_sheet.png"))
        self.image = self.spritesheet.get_image(0,0,TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK) # set black pixels invisible
        # self.image = pg.Surface((TILESIZE, TILESIZE))
        # self.image.fill(WHITE)

        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT

        self.vel = vec(0,0)
        self.pos = vec(x * TILESIZE,y * TILESIZE)

        self.facing_dir = 1 # 1 is right, 0 center, -1 left
        self.previous_dir = 1

        # animation stuff
        self.last_update = 0
        self.current_frame = 0
        self.load_images()

        self.touching_ground = False

    def get_keys(self):
        # reset v so it doesnt fly away
        # listen for events specific to keys
        # change velocity based on which key is pressed
        self.state = "idle"

        self.vel = vec(0,self.vel.y)
        keys = pg.key.get_pressed() # get pressed keys

        self.previous_dir = self.facing_dir

        if keys[pg.K_LEFT] or keys[pg.K_a]: # left
            self.vel.x = -PLAYER_SPEED
            self.state = "walking"
            self.facing_dir = -1
        if keys[pg.K_RIGHT] or keys[pg.K_d]: # right
            self.vel.x = PLAYER_SPEED
            self.state = "walking"
            self.facing_dir = 1

        # if keys[pg.K_DOWN] or keys[pg.K_s]: # down
        #     self.vel.y = PLAYER_SPEED 
        # if keys[pg.K_UP] or keys[pg.K_w]:# and self.touching_ground # up
        #     self.vel.y = -PLAYER_SPEED

        justpressedkeys = pg.key.get_just_pressed()

        if (justpressedkeys[pg.K_UP] or justpressedkeys[pg.K_w]) and self.touching_ground:
            self.vel.y -= PLAYER_JUMP
            self.touching_ground = False
            self.state = "jumping"
        elif not self.touching_ground:
            self.vel.y += GRAVITY * self.game.dt
            self.state = "falling"


    def handle_collision(self):
        mob_hits = pg.sprite.spritecollide(self, self.game.all_mobs, False)

        if mob_hits:
            mob_hits[0].kill()
            # print("killed em")

    def animate(self):
        # use the time element to get now
        if (self.state == "idle"):
            self.animateFrames(self.idle_frames)
        elif (self.state == "walking" and self.touching_ground):
            self.animateFrames(self.walk_frames)
        elif (self.state == "falling"):
            self.animateFrames(self.fall_frames)
        elif (self.state == "jumping"):
            self.animateFrames(self.jump_frames)

    def animateFrames(self, frames):
        now = pg.time.get_ticks()

        if now - self.last_update > 125:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(frames) # loop the frames
            bottom = self.rect.bottom
            self.image = frames[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
            if self.facing_dir == -1: # if our direction is not the default (1 facing right)
                self.image = pg.transform.flip(self.image, True, False) # flip it



    def load_images(self):
        self.idle_frames = [self.spritesheet.get_image(0,0,TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)
                            ]
        
        self.walk_frames = [self.spritesheet.get_image(TILESIZE * 4, 0 ,TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE * 5, 0 ,TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE * 6, 0 ,TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE * 5, 0 ,TILESIZE, TILESIZE)
                            ]

        self.jump_frames = [self.spritesheet.get_image(TILESIZE * 2, 0, TILESIZE, TILESIZE)]
        self.fall_frames = [self.spritesheet.get_image(TILESIZE * 3, 0, TILESIZE, TILESIZE)]
    
    def update(self):
        self.get_keys()

        self.animate()
        
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y-floor')
        collide_with_walls(self, self.game.all_walls, 'y-ciel')
        self.rect.center = self.hit_rect.center
        
        self.handle_collision()


class Wall(Sprite):
    def __init__(self, game, x, y):
        # put it in the all sprites group immediately
        self.groups = game.all_sprites, game.all_walls

        Sprite.__init__(self, self.groups) # initialize sprite

        self.game = game # allow the wall to access game

        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHT_GREEN)

        self.rect = self.image.get_rect()

        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.rect.x = self.x
        self.rect.y = self.y

class Mob(Sprite):
    def __init__(self, game, x, y, color):
        # put it in the all sprites group immediately
        self.groups = game.all_sprites, game.all_mobs

        Sprite.__init__(self, self.groups) # initialize sprite

        self.game = game # allow the mob to access game

        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)

        self.rect = self.image.get_rect()

        self.stored_speed = MOB_SPEED

        self.vx, self.vy = self.stored_speed, self.stored_speed

        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.rect.x = self.x
        self.rect.y = self.y

    def handle_collision(self, axis):
        wall_hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        mob_hits = pg.sprite.spritecollide(self, self.game.all_mobs, False)
        
        if wall_hits:
            # self.stored_speed = min(self.stored_speed *  BOUNCE_FACTOR, MOB_MAX_SPEED)
            if axis == "x": # only checking x axis
                if self.vx > 0: # moving right
                    # move it out of the wall so it doesnt detect twice
                    self.rect.right = wall_hits[0].rect.left
                    self.vx = -self.stored_speed
                    return
                if self.vx < 0: # moving left
                    self.rect.left = wall_hits[0].rect.right
                    self.vx = self.stored_speed
                    return
                return
            elif axis == "y": # only checking y axis
                if self.vy > 0: # moving up
                    self.rect.bottom = wall_hits[0].rect.top
                    self.vy = -self.stored_speed
                    return
                if self.vy < 0: # moving down
                    self.rect.top = wall_hits[0].rect.bottom
                    self.vy = self.stored_speed
                    return
            

    def update(self):
        # if self.rect.right > SCREEN_WIDTH or self.rect.x < 0:
        #     self.vx *= -1
        # if self.rect.bottom > SCREEN_HEIGHT or self.rect.y < 0:
        #     self.vy *= -1

        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt

        self.rect.x = self.x # move visual x to stored x
        self.handle_collision("x")
        self.rect.y = self.y # move visual y to stored y
        self.handle_collision("y")