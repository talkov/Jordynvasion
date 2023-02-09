import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard
from boss import Boss
from buffs import Buffs
import random

class JordiInvasion:
    """Overall class to manage assets and behaviour."""

    def __init__(self):
        """Initialize the game, create game recourses"""
        pygame.init()
        self.settings = Settings()
        self.boss_level = False
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Jordiz Invasion")

        # Create an instance to store game statistics.
        # and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.buffs = pygame.sprite.Group()
        self._create_fleet()
        self.boss_levels_list = [3,5,7]
        self.current_buff = []
        self.buff_on_screen = False
        # Make the Play button.
        self.play_button = Button(self, "Test Yourself")

        # set the background color.
        self.bg_color = (230, 230, 230,)

        # hit counter for bosses
        self.hitCounter = 0

        #for the third buff
        self.thirdBuff = True

    def run_game(self):
        """Start the main loop for the game"""
        while True:
            self._check_events()
            if self.stats.game_active:
                if self.stats.level in self.boss_levels_list:
                    self.boss_level = True
                else:
                    self.boss_level = False
                # self.Buffd()
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                # self._update_buff()
            self._update_screen()

    def _check_events(self):
        """respond to keypress and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when player clicks Play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset game settings
            self.settings.initialize_dynamic_settings()

            # Reset game stats.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)


    def _check_keydown_events(self, event):
        """respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of the bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet alien collisions."""
        # Remove any bullets and aliens that have collided, if buff number 3 is off
        if self.boss_level:
            collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, False)
        else:
            collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, self.thirdBuff, True)
        if collisions:
            if self.boss_level:
                for boss in self.aliens.sprites():
                    self._boss_fight(boss)
                    self.hitCounter += 1
            else:
                for aliens in collisions.values():
                    self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            if (self.stats.level + 1) in self.boss_levels_list:
                self._create_Boss()
                boss_level = True
            else:
                self._create_fleet()
            self.settings.increase_speed()
            # Increase level
            self.stats.level += 1
            self.sb.prep_level()

    # def _check_buffs_ship_collisions(self):
    #     buff_collide = pygame.sprite.spritecollide(self.ship,self.buffs, True)
    #     if buff_collide:
    #         buff_collide[0].collision(self)
    #         self.buff_on_screen = False
    #         self.current_buff.append(buff_collide[0])
    #         buff_collide[0].kill()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien"""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as ship got hit.
                self._ship_hit()
                break

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update all the
        positions of the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Create the fleet of aliens."""
        if self.boss_level:
            self._create_Boss()
        else:
            # Create an alien and find the number of aliens in a row
            # Spacing between each alien is equal to one alien width
            alien = Alien(self)     # Make an alien
            alien_width, alien_height = alien.rect.size
            available_space_x = self.settings.screen_width - (2 * alien_width)
            number_aliens_x = available_space_x // (2 * alien_width)

            # Determine the number of rows of aliens that fit on the screen
            ship_height = self.ship.rect.height
            available_space_y = (self.settings.screen_height - (3 * alien_height)
                                 - ship_height)
            number_rows = available_space_y // (2 * alien_height)

            # Create the full fleet of aliens.
            for row_number in range(number_rows):
                for alien_number in range(number_aliens_x):
                    self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _create_Boss(self):
        if self.stats.level + 1 == 3:
            boss = Boss(self,50,1)
        elif self.stats.level + 1 == 5:
            boss = Boss(self, 75, 2)
        elif self.stats.level + 1 == 7:
            boss = Boss(self, 100, 3)

        self.aliens.add(boss)  # Make a boss alien
        self.hitCounter = 0


    def _boss_fight(self,boss):
        if boss.life == self.hitCounter:
            self.boss_level = False
            self.aliens.empty()
            self.stats.score += 1000

    # def _create_buff(self):
    #     timeForBuff = False
    #     #make sure the ship is not buffed
    #     # if not self._check_if_buffd():
    #     if True:
    #         #randomly pick a time fir a buff
    #         timeForBuff = random.choices(population=[True,False], weights=[1, 0], k=1)[0]
    #         if timeForBuff and (not self.buff_on_screen):
    #             self.buff_on_screen = True
    #             buff = Buffs(self)
    #             self.buffs.add(buff)
    #     return timeForBuff

    #
    # def _check_if_buffd(self):
    #     #check if the ship has a buff
    #     if self.current_buff == []:
    #         self.buffs.empty()
    #         self.settings.bullets_allowed = 3
    #         self.thirdBuff = True
    #         self.settings.ship_speed = 1.5
    #         buffed = False
    #     else:
    #         buffed = True
    #         # if buffed make the needed changes
    #         if self.current_buff != []:
    #             for buff in self.current_buff:
    #                 buff.Buffed()
    #     return buffed
    #
    # def end_buffs(self):
    #     self.settings.bullets_allowed = 3
    #     self.thirdBuff = True
    #     self.settings.ship_speed = 1.5
    #
    # def _update_buff(self):
    #     self.buffs.update(self)
    #     # Get rid of buffs that have disappeared.
    #     for buff in self.buffs.copy():
    #         if buff.rect.bottom >= 800:
    #             self.bullets.remove(buff)
    #             self.buff_on_screen = False
    #         else:
    #             self._check_buffs_ship_collisions()

    def _update_screen(self):
        """Update images on screen, and flip to new screen."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        #Draw buffs
        # if self._create_buff():
        #     self.buffs.draw(self.screen)
        # if not self.current_buff:
        #     self.end_buffs()
        #Draw the score information
        self.sb.show_score()
        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ji = JordiInvasion()
    ji.run_game()
