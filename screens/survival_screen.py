import pygame
import random
from screens.base_game_screen import BaseGameScreen
from entities.unit import Unit


class SurvivalScreen(BaseGameScreen):
    """
    Survival mode game screen.

    In this mode:
    - There is no enemy base (endless survival gameplay)
    - The player survives against continuous waves of enemies
    - Difficulty increases over time through waves
    - Enemy spawn rate and evolution scale dynamically
    """

    def __init__(self, game_engine):
        super().__init__(game_engine)

        # =========================
        # Background Setup
        # =========================
        bg_path = "assets/images/screens/ogs_arena.png"
        original_bg = pygame.image.load(bg_path)

        # Scale background to fit screen resolution
        self.bg_img = pygame.transform.scale(
            original_bg,
            (self.game.WIDTH, self.game.HEIGHT)
        )

        # No enemy base in survival mode
        self.enemy_base_rect = None

        # =========================
        # Timing System
        # =========================
        self.start_time = pygame.time.get_ticks()
        self.last_wave_time = pygame.time.get_ticks()
        self.last_enemy_spawn_time = pygame.time.get_ticks()

        # Wave system
        self.wave = 1
        self.next_wave_delay = 20000  # 20 seconds per wave

        # =========================
        # Difficulty Configuration
        # =========================
        self.difficulty = self.game.settings.get("difficulty", "normal")

        # Adjust enemy spawn speed based on difficulty
        if self.difficulty == "easy":
            self.base_spawn_delay = 4000
            self.spawn_decrease = 200

        elif self.difficulty == "hard":
            self.base_spawn_delay = 2000
            self.spawn_decrease = 400

        else:  # normal
            self.base_spawn_delay = 3000
            self.spawn_decrease = 300

        # Current dynamic spawn delay
        self.enemy_spawn_delay = self.base_spawn_delay

    # =========================
    # Game Update Loop
    # =========================
    def update(self, dt):
        """
        Updates survival mode logic:
        - Wave progression system
        - Enemy evolution scaling
        - Continuous enemy spawning
        """
        super().update(dt)
        current_time = pygame.time.get_ticks()

        # =========================
        # Wave Progression System
        # =========================
        if current_time - self.last_wave_time > self.next_wave_delay:
            self.wave += 1
            self.last_wave_time = current_time

            # Increase difficulty by reducing spawn delay
            self.base_spawn_delay = max(
                500,
                self.base_spawn_delay - self.spawn_decrease
            )

            # Enemy evolution rate depends on difficulty
            evolution_rate = 3

            if self.difficulty == "hard":
                evolution_rate = 2
            elif self.difficulty == "easy":
                evolution_rate = 4

            # Advance enemy age (max 3 stages)
            if self.wave % evolution_rate == 0 and self.enemy_age_index < 3:
                self.enemy_age_index += 1

        # =========================
        # Enemy Spawning System
        # =========================
        if current_time - self.last_enemy_spawn_time > self.enemy_spawn_delay:

            # Unit type selection based on enemy age
            if self.enemy_age_index == 0:
                enemy_type = random.choice(["melee", "melee", "ranged"])
            else:
                if self.difficulty == "hard":
                    enemy_type = random.choice(
                        ["melee", "ranged", "flying", "flying"]
                    )
                else:
                    enemy_type = random.choice(
                        ["melee", "ranged", "flying"]
                    )

            current_enemy_age = self.ages[self.enemy_age_index]

            # Spawn enemy outside screen (right side)
            self.units.append(Unit(
                self.game.WIDTH + 50,
                self.player_base_rect.bottom - 150,
                "enemy",
                80,
                (255, 0, 0),
                enemy_type,
                current_enemy_age
            ))

            # Reset spawn timer
            self.last_enemy_spawn_time = current_time

            # Add randomness to spawn timing for more natural behavior
            self.enemy_spawn_delay = self.base_spawn_delay + random.randint(-500, 500)

    # =========================
    # Rendering
    # =========================
    def draw(self):
        """
        Renders survival mode UI:
        - Timer
        - Wave counter
        - Difficulty indicator
        """
        super().draw()

        # =========================
        # Survival Time Tracking
        # =========================
        current_time = pygame.time.get_ticks()
        survived_seconds = (current_time - self.start_time) // 1000

        minutes = survived_seconds // 60
        seconds = survived_seconds % 60

        # Time display text
        time_text = self.font.render(
            f"TIME: {minutes:02d}:{seconds:02d}",
            True,
            (255, 255, 255)
        )

        # Wave + difficulty display
        diff_text = self.difficulty.upper()
        wave_text = self.font.render(
            f"WAVE: {self.wave} ({diff_text})",
            True,
            (255, 50, 50)
        )

        # =========================
        # UI Background Panel
        # =========================
        bg_rect = pygame.Rect(
            self.game.WIDTH // 2 - 100,
            10,
            260,
            80
        )

        # Semi-transparent background for readability
        s = pygame.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(150)
        s.fill((0, 0, 0))
        self.game.screen.blit(s, (bg_rect.x, bg_rect.y))

        # =========================
        # UI Text Rendering
        # =========================
        self.game.screen.blit(time_text, (self.game.WIDTH // 2 - 50, 20))
        self.game.screen.blit(wave_text, (self.game.WIDTH // 2 - 80, 55))