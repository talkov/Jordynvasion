from alien import Alien
import pygame

class Boss(Alien):
    def __init__(self,ji_game,life,which_boss):
        """Initialize the Boss and set it's starting position"""
        super().__init__(ji_game)
        self.screen = ji_game.screen
        self.settings = ji_game.settings
        self.life = life


        # Load the alien image and set it's rect attribute.
        if which_boss == 1:
            self.image = pygame.image.load('images/leaf_boss.bmp')
        elif which_boss == 2:
            self.image = pygame.image.load('images/green_boss.bmp')
        elif which_boss == 3:
            self.image = pygame.image.load('images/skull_boss.bmp')
        self.rect = self.image.get_rect()



    def hit(self):
        self.life -= 1