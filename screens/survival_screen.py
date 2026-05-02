import pygame
import random
from screens.base_game_screen import BaseGameScreen
from entities.unit import Unit


class SurvivalScreen(BaseGameScreen):
    def __init__(self, game_engine):
        super().__init__(game_engine)

        bg_path = "assets/images/screens/ogs_arena.png"

        original_bg = pygame.image.load(bg_path)

        self.bg_img = pygame.transform.scale(original_bg, (self.game.WIDTH, self.game.HEIGHT))

        self.enemy_base_rect = None  # אין בסיס אויב במצב הישרדות
        # משתני זמן וגלים
        self.start_time = pygame.time.get_ticks()
        self.last_wave_time = pygame.time.get_ticks()
        self.last_enemy_spawn_time = pygame.time.get_ticks()

        self.wave = 1
        self.next_wave_delay = 20000  # כל 20 שניות (20,000 מילישניות) עולים גל

        # --- קריאת רמת הקושי מההגדרות ---
        self.difficulty = self.game.settings.get("difficulty", "normal")

        # התאמת קצב יציאת האויבים לפי רמת הקושי
        if self.difficulty == "easy":
            self.base_spawn_delay = 4000  # יוצאים לאט יותר (כל 4 שניות)
            self.spawn_decrease = 200  # הקצב עולה במעט כל גל
        elif self.difficulty == "hard":
            self.base_spawn_delay = 2000  # יוצאים מהר מאוד (כל 2 שניות)
            self.spawn_decrease = 400  # הקצב עולה באגרסיביות כל גל
        else:  # normal
            self.base_spawn_delay = 3000
            self.spawn_decrease = 300

        self.enemy_spawn_delay = self.base_spawn_delay

    def update(self,dt):
        super().update(dt)
        current_time = pygame.time.get_ticks()

        # --- ניהול גלים ורמת קושי ---
        if current_time - self.last_wave_time > self.next_wave_delay:
            self.wave += 1
            self.last_wave_time = current_time

            # בכל גל, האויבים יוצאים מהר יותר (אבל לא פחות מ-חצי שניה כדי שהמשחק לא יקרוס)
            self.base_spawn_delay = max(500, self.base_spawn_delay - self.spawn_decrease)

            # קצב ההתפתחות לעידן הבא לפי הקושי
            evolution_rate = 3  # ברירת מחדל - כל 3 גלים
            if self.difficulty == "hard":
                evolution_rate = 2  # ב-Hard מתפתחים מהר יותר
            elif self.difficulty == "easy":
                evolution_rate = 4  # ב-Easy מתפתחים לאט יותר

            if self.wave % evolution_rate == 0 and self.enemy_age_index < 3:
                self.enemy_age_index += 1

        # --- זימון אויבים ---
        if current_time - self.last_enemy_spawn_time > self.enemy_spawn_delay:
            # בעידן הראשון לא מוציאים מעופפים
            if self.enemy_age_index == 0:
                enemy_type = random.choice(["melee", "melee", "ranged"])
            else:
                # ב-Hard יש סיכוי כפול לאויב מעופף!
                if self.difficulty == "hard":
                    enemy_type = random.choice(["melee", "ranged", "flying", "flying"])
                else:
                    enemy_type = random.choice(["melee", "ranged", "flying"])

            current_enemy_age = self.ages[self.enemy_age_index]

            # זימון החייל מחוץ למסך מימין
            self.units.append(
                Unit(self.game.WIDTH + 50, self.player_base_rect.bottom - 150, "enemy", 80, (255, 0, 0), enemy_type,
                     current_enemy_age))

            self.last_enemy_spawn_time = current_time

            # אקראיות קלה ברווח בין האויבים
            self.enemy_spawn_delay = self.base_spawn_delay + random.randint(-500, 500)

    def draw(self):
        super().draw()

        # --- תצוגת זמן וגל למעלה באמצע המסך ---
        current_time = pygame.time.get_ticks()
        survived_seconds = (current_time - self.start_time) // 1000
        minutes = survived_seconds // 60
        seconds = survived_seconds % 60

        time_text = self.font.render(f"TIME: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))

        # מציגים את מספר הגל יחד עם רמת הקושי שמופעלת כרגע
        diff_text = self.difficulty.upper()
        wave_text = self.font.render(f"WAVE: {self.wave} ({diff_text})", True, (255, 50, 50))

        # ציור רקע שחור חצי-שקוף
        bg_rect = pygame.Rect(self.game.WIDTH // 2 - 100, 10, 260, 80)
        s = pygame.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(150)
        s.fill((0, 0, 0))
        self.game.screen.blit(s, (bg_rect.x, bg_rect.y))

        # ציור הטקסט
        self.game.screen.blit(time_text, (self.game.WIDTH // 2 - 50, 20))
        self.game.screen.blit(wave_text, (self.game.WIDTH // 2 - 80, 55))