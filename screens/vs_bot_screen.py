import pygame
import random
from screens.base_game_screen import BaseGameScreen
from entities.unit import Unit


class VsBotScreen(BaseGameScreen):
    """
    Game screen for single-player mode against AI (bot).

    Responsibilities:
    - Manage enemy base state and difficulty scaling
    - Control enemy unit spawning logic
    - Handle enemy age progression
    - Render enemy base and health bar
    """

    def __init__(self, game_engine):
        super().__init__(game_engine)

        # =========================
        # Difficulty Configuration
        # =========================
        self.difficulty = self.game.settings.get("difficulty", "normal")

        # Configure bot behavior based on difficulty level
        if self.difficulty == "easy":
            self.enemy_max_hp = 800
            self.enemy_evolve_delay = 60000  # slower evolution
            self.spawn_range = (10000, 15000)

        elif self.difficulty == "hard":
            self.enemy_max_hp = 1300
            self.enemy_evolve_delay = 30000  # faster evolution
            self.spawn_range = (4000, 7000)

        else:  # normal difficulty
            self.enemy_max_hp = 1000
            self.enemy_evolve_delay = 45000
            self.spawn_range = (7000, 12000)

        # Initial enemy base health
        self.enemy_base_hp = self.enemy_max_hp

        # =========================
        # Enemy Base Position
        # =========================
        # Position of the enemy base on screen (right side, slightly raised)
        self.enemy_base_rect = pygame.Rect(
            self.game.WIDTH - 400,
            self.game.HEIGHT - 650,
            700,
            600
        )

        # =========================
        # Timing Controls
        # =========================
        self.last_enemy_evolve_time = pygame.time.get_ticks()
        self.last_enemy_spawn_time = pygame.time.get_ticks()
        self.enemy_spawn_delay = self.spawn_range[0]

    # =========================
    # Game Update Loop
    # =========================
    def update(self, dt):
        """
        Updates enemy AI logic every frame.

        Handles:
        - Enemy age evolution over time
        - Enemy unit spawning with randomized timing
        """
        super().update(dt)
        current_time = pygame.time.get_ticks()

        # =========================
        # Enemy Age Progression
        # =========================
        # Enemy evolves to stronger ages over time
        if self.enemy_age_index < 3 and current_time - self.last_enemy_evolve_time > self.enemy_evolve_delay:
            self.enemy_age_index += 1
            self.last_enemy_evolve_time = current_time

        # =========================
        # Enemy Unit Spawning
        # =========================
        if current_time - self.last_enemy_spawn_time > self.enemy_spawn_delay:

            # Determine possible unit types based on age and difficulty
            if self.enemy_age_index == 0:
                spawn_options = ["melee", "melee", "ranged"]
            else:
                if self.difficulty == "hard":
                    spawn_options = ["melee", "ranged", "flying", "flying"]
                else:
                    spawn_options = ["melee", "melee", "ranged", "flying"]

            enemy_type = random.choice(spawn_options)
            current_enemy_age = self.ages[self.enemy_age_index]

            # Spawn enemy unit near enemy base
            self.units.append(Unit(
                self.enemy_base_rect.right - 350,
                self.enemy_base_rect.bottom - 150,
                "enemy",
                80,
                (255, 0, 0),
                enemy_type,
                current_enemy_age
            ))

            # Reset spawn timer with random delay
            self.last_enemy_spawn_time = current_time
            self.enemy_spawn_delay = random.randint(
                self.spawn_range[0],
                self.spawn_range[1]
            )

    # =========================
    # Rendering
    # =========================
    def draw(self):
        """
        Renders enemy base, UI elements, and health bar.
        """
        super().draw()

        # =========================
        # Enemy Base Rendering
        # =========================
        enemy_age_name = self.ages[self.enemy_age_index]
        enemy_base_img = self.base_images.get(enemy_age_name)

        if enemy_base_img:
            # Flip image so enemy base faces the player
            enemy_base_img_flipped = pygame.transform.flip(enemy_base_img, True, False)
            self.game.screen.blit(enemy_base_img_flipped, self.enemy_base_rect)

        # =========================
        # Enemy Health Bar
        # =========================
        e_hp_bar_width = 200
        e_hp_bar_height = 20
        e_hp_bar_x = self.enemy_base_rect.right - 550
        e_hp_bar_y = self.enemy_base_rect.y - 30

        # Calculate health percentage
        e_hp_ratio = max(0, self.enemy_base_hp / self.enemy_max_hp)

        # Background (red = missing HP)
        pygame.draw.rect(
            self.game.screen,
            (255, 0, 0),
            (e_hp_bar_x, e_hp_bar_y, e_hp_bar_width, e_hp_bar_height)
        )

        # Foreground (green = remaining HP)
        pygame.draw.rect(
            self.game.screen,
            (0, 255, 0),
            (e_hp_bar_x, e_hp_bar_y, e_hp_bar_width * e_hp_ratio, e_hp_bar_height)
        )

        # Border
        pygame.draw.rect(
            self.game.screen,
            (0, 0, 0),
            (e_hp_bar_x, e_hp_bar_y, e_hp_bar_width, e_hp_bar_height),
            2
        )