import pygame as pg
from settings import *
from playerResource import * # access player resource
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
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        
        if hits:
            # if we are colliding from the right
            if hits[0].rect.centery > sprite.hit_rect.centery:
                # reposition sprite to the left side of the wall
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
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

        if (keys[pg.K_UP] or keys[pg.K_w]) and self.touching_ground: # if up is pressed and touching ground
            self.vel.y -= PLAYER_JUMP
            self.touching_ground = False
            self.state = "jumping"
        elif not self.touching_ground:
            self.vel.y += GRAVITY * self.game.dt
            self.state = "falling"


        # if keys[pg.K_DOWN] or keys[pg.K_s]: # down
        #     self.vel.y = PLAYER_SPEED 
        # if keys[pg.K_UP] or keys[pg.K_w]:# and self.touching_ground # up
        #     self.vel.y = -PLAYER_SPEED

        # justpressedkeys = pg.key.get_just_pressed()

        # if (justpressedkeys[pg.K_UP] or justpressedkeys[pg.K_w]) and self.touching_ground:
        #     self.vel.y -= PLAYER_JUMP
        #     self.touching_ground = False
        #     self.state = "jumping"
        # elif not self.touching_ground:
        #     self.vel.y += GRAVITY * self.game.dt
        #     self.state = "falling"

    def handle_collision(self):
        mob_hits = pg.sprite.spritecollide(self, self.game.all_mobs, False)
        collectable_hits = pg.sprite.spritecollide(self, self.game.all_collectables, False)

        if mob_hits:
            mob_hits[0].kill()
            # print("killed em")
        
        if collectable_hits:
            hit = collectable_hits[0]
            COLLECTED[hit.collectableID] += hit.value # add value to dict by id
            hit.kill() # get rid of coin
            self.game.score += 1
            self.game.coin_collect.play()


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

        self.pos = vec(self.x, self.y)

        self.rect.x = self.x
        self.rect.y = self.y

        # self.camera_offset = self.pos - self.game.camera.pos
        
class Mob(Sprite):
    def __init__(self, game, x, y):
        # put it in the all sprites group immediately
        self.groups = game.all_sprites, game.all_mobs

        Sprite.__init__(self, self.groups) # initialize sprite

        self.game = game # allow the mob to access game

        self.image = pg.Surface((TILESIZE, TILESIZE))

        self.rect = self.image.get_rect()

        self.speed = MOB_SPEED

        self.spritesheet = Spritesheet(path.join(self.game.image_dir, "enemy.png"))
        self.image = self.spritesheet.get_image(0,0,TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK) # set black pixels invisible
        
        self.last_update = 0
        self.current_frame = 0
        self.load_images()

        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.pos = vec(self.x, self.y)
        self.vel = vec(0,0)

        self.rect.x = self.x
        self.rect.y = self.y

        self.hit_rect = MOB_HIT_RECT

        self.player = 0

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
                
    # uses autocomplete by creating a chase method using pos vectors and chase obj
    def chase(self, obj):
        if self.pos.x < obj.pos.x:
            self.vel.x = self.speed
            self.dir = "right"
        elif self.pos.x > obj.pos.x:
            self.vel.x = -self.speed
            self.dir = "left"
        else:
            self.vel.x = 0

        if self.pos.y < obj.pos.y:
            self.vel.y = self.speed
        elif self.pos.y > obj.pos.y:
            self.vel.y = -self.speed
        else:
            self.vel.y = 0

    def update(self):
        if self.player == 0:
            self.player =  self.game.player

        self.chase(self.game.player)
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')

class Collectable(Sprite): # later on... sprite instead of color
    def __init__(self, game, x, y, color, collectableID, value):
        self.groups = game.all_sprites, game.all_collectables
        Sprite.__init__(self, self.groups) # initialize sprite
        self.game = game # allow the wall to access game

        self.collectableID = collectableID # use an id for multiple collectable types
        self.value = value

        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.pos = vec(self.x, self.y)
        self.rect.x = self.x
        self.rect.y = self.y


class Camera(Sprite):
    def __init__(self, game, x, y, color):
            # put it in the all sprites group immediately
            self.groups = game.all_sprites
    
            Sprite.__init__(self, self.groups) # initialize sprite
    
            self.game = game # allow the mob to access game
    
            self.image = pg.Surface((TILESIZE, TILESIZE))
            self.image.fill(color)
    
            self.rect = self.image.get_rect()
    
            self.x = x * TILESIZE
            self.y = y * TILESIZE

            self.pos = vec(self.x,self.y)
    
            self.rect.x = self.x
            self.rect.y = self.y

            self.player = 0

    def update(self):
        if self.player == 0:
            self.player = self.game.player

        self.pos = self.player.pos
        self.rect = self.player.rect