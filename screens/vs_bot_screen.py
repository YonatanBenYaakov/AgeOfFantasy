import pygame
import random
from screens.base_game_screen import BaseGameScreen
from entities.unit import Unit

class VsBotScreen(BaseGameScreen):
    def __init__(self, game_engine):
        super().__init__(game_engine)

        self.difficulty = self.game.settings.get("difficulty", "normal")

        # הגדרת משתני מקסימום חיים (כדי לחשב את מד החיים של האויב)
        if self.difficulty == "easy":
            self.enemy_max_hp = 800
            self.enemy_evolve_delay = 60000
            self.spawn_range = (10000, 15000)
        elif self.difficulty == "hard":
            self.enemy_max_hp = 1300
            self.enemy_evolve_delay = 30000
            self.spawn_range = (4000, 7000)
        else:  # normal
            self.enemy_max_hp = 1000
            self.enemy_evolve_delay = 45000
            self.spawn_range = (7000, 12000)

        # טעינת החיים לפי המקסימום שנקבע
        self.enemy_base_hp = self.enemy_max_hp

        # הרמנו את הבסיס למעלה (מ-580 ל-650)
        self.enemy_base_rect = pygame.Rect(self.game.WIDTH - 400, self.game.HEIGHT - 650, 700, 600)

        self.last_enemy_evolve_time = pygame.time.get_ticks()
        self.last_enemy_spawn_time = pygame.time.get_ticks()
        self.enemy_spawn_delay = self.spawn_range[0]

    def update(self,dt):
        super().update(dt)
        current_time = pygame.time.get_ticks()

        if self.enemy_age_index < 3 and current_time - self.last_enemy_evolve_time > self.enemy_evolve_delay:
            self.enemy_age_index += 1
            self.last_enemy_evolve_time = current_time

        if current_time - self.last_enemy_spawn_time > self.enemy_spawn_delay:
            if self.enemy_age_index == 0:
                spawn_options = ["melee", "melee", "ranged"]
            else:
                if self.difficulty == "hard":
                    spawn_options = ["melee", "ranged", "flying", "flying"]
                else:
                    spawn_options = ["melee", "melee", "ranged", "flying"]

            enemy_type = random.choice(spawn_options)
            current_enemy_age = self.ages[self.enemy_age_index]

            # הרמנו גם את הספאון של בוט האויב
            self.units.append(Unit(
                self.enemy_base_rect.right - 350,
                self.enemy_base_rect.bottom - 150,
                "enemy", 80, (255, 0, 0), enemy_type, current_enemy_age
            ))

            self.last_enemy_spawn_time = current_time
            self.enemy_spawn_delay = random.randint(self.spawn_range[0], self.spawn_range[1])

    def draw(self):
        super().draw()

        enemy_age_name = self.ages[self.enemy_age_index]
        enemy_base_img = self.base_images.get(enemy_age_name)
        if enemy_base_img:
            enemy_base_img_flipped = pygame.transform.flip(enemy_base_img, True, False)
            self.game.screen.blit(enemy_base_img_flipped, self.enemy_base_rect)

        # ==============================
        # מד חיים (Health Bar) לאויב
        # ==============================
        e_hp_bar_width = 200
        e_hp_bar_height = 20
        e_hp_bar_x = self.enemy_base_rect.right - 550
        e_hp_bar_y = self.enemy_base_rect.y - 30

        e_hp_ratio = max(0, self.enemy_base_hp / self.enemy_max_hp)

        pygame.draw.rect(self.game.screen, (255, 0, 0), (e_hp_bar_x, e_hp_bar_y, e_hp_bar_width, e_hp_bar_height))
        pygame.draw.rect(self.game.screen, (0, 255, 0),
                         (e_hp_bar_x, e_hp_bar_y, e_hp_bar_width * e_hp_ratio, e_hp_bar_height))
        pygame.draw.rect(self.game.screen, (0, 0, 0), (e_hp_bar_x, e_hp_bar_y, e_hp_bar_width, e_hp_bar_height), 2)
