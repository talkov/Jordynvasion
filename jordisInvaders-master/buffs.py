from pygame.locals import *
import pygame
import time
import os
from settings import Settings
import random



# list of buffs
# 1 - infinite bullets for 5 seconds
# 2 - one more life
# 3 - bullets won't disappear after hit for 5 seconds
# 4 - slows down the ship


class Buffs(pygame.sprite.Sprite):
    def __init__(self,ji_game):
        """Initialize the alien and set it's starting position"""
        super().__init__()
        self.screen = ji_game.screen
        self.settings = ji_game.settings
        self.screen_rect = ji_game.screen.get_rect()
        self.start_time = False
        # make it a sprite
        pygame.sprite.Sprite.__init__(self)

        # choose random buff type
        if ji_game.stats.ships_left < 3:
            self.which_buff = random.choices(population=[1, 2, 3, 4], weights=[0.25, 0.25, 0.25, 0.25], k=1)[0]
        else:
            self.which_buff = random.choices(population=[1, 3, 4], weights=[0.33, 0.33, 0.33], k=1)[0]
        # buff 1
        if self.which_buff == 1:
            self.image = pygame.image.load('images/infinite_bullet_buff.bmp')
            self.rect = self.image.get_rect()
            self.buff_duration = 5
        # buff 2
        elif self.which_buff == 2:
            self.image = pygame.image.load('images/ship.bmp')
            self.rect = self.image.get_rect()
            self.buff_duration = 1
        # buff 3
        elif self.which_buff == 3:
            self.image = pygame.image.load('images/bullet_buff.bmp')
            self.rect = self.image.get_rect()
            self.buff_duration = 5
        # buff 4
        elif self.which_buff == 4:
            self.image = pygame.image.load('images/slow_down_buff.bmp')
            self.rect = self.image.get_rect()
            self.buff_duration = 5

        # Start every buff from the top
        self.rect.top = self.screen_rect.top
        # Store buff position as a decimal value
        self.y = float(self.rect.y)
        self.rect.x = random.randrange(10, self.screen.get_size()[0]-20)




    def update(self,ji_game):
        #move rect each update (can be adjusted)
        self.y += self.settings.buffs_speed
        # Update the rect position
        self.rect.y = self.y
        #if it goes to to the bottom of the screen delete it
        if self.rect.y > self.settings.screen_height:
            self.kill()
            ji_game.buff_on_screen = False
            ji_game.buffs.empty()
        # check if the buff collided and didn't expired
        if self.start_time and self.buff_duration <= int(time.time() - self.start_time):
            self.kill()
            ji_game.buffs.empty()
            ji_game.current_buff.clear()
            ji_game.end_buffs()
        else: 
            self.Buffed(ji_game)



    def collision(self,ji_game):
        self.start_time = time.time()
        self.kill()
        self.Buffed(ji_game)



    def Buffed(self,ji_game):
        for buff in ji_game.buffs.sprites():
            if buff.which_buff == 1:
                ji_game.settings.bullets_allowed = 100000
            elif buff.which_buff == 2 and ji_game.stats.ships_left < 3:
                ji_game.stats.ships_left += 1
            elif buff.which_buff == 3:
                ji_game.thirdBuff = False
            elif buff.which_buff == 4:
                ji_game.settings.ship_speed = 0.25






