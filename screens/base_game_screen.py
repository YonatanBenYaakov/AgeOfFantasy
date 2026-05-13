import pygame
import random
import os
from engine.screen import Screen
from engine.button import Button
from entities.unit import Unit
from entities.projectile import Projectile
from screens.game_over_screen import GameOverScreen


class BaseTarget:
    """
    Fake target wrapper used so projectiles can treat bases like units.
    This allows unified combat logic between units and bases.
    """

    def __init__(self, rect, team, screen):
        self.rect = rect
        self.team = team
        self.screen = screen
        self.is_flying = False
        self.unit_type = "base"

    @property
    def hp(self):
        # Redirect HP access to the correct base (player or enemy)
        return self.screen.player_base_hp if self.team == "player" else self.screen.enemy_base_hp

    @hp.setter
    def hp(self, value):
        # Update HP directly on the screen
        if self.team == "player":
            self.screen.player_base_hp = value
        else:
            self.screen.enemy_base_hp = value


class BaseGameScreen(Screen):
    """
    Core gameplay class shared by all game modes.
    Handles:
    - Unit combat logic
    - Base attacks
    - Projectiles
    - Resources (gold, XP)
    - Win/Lose conditions
    """

    def __init__(self, game_engine):
        super().__init__(game_engine)

        # =========================
        # MUSIC SETUP
        # =========================
        music_path = "assets/music/game_music.mp3"

        if self.game.settings.get("music_on", True):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Could not load game music: {e}")

        # =========================
        # BACKGROUND
        # =========================
        bg_path = "assets/images/screens/human_arena.png"
        try:
            original_bg = pygame.image.load(bg_path)
            self.bg_img = pygame.transform.scale(original_bg, (self.game.WIDTH, self.game.HEIGHT))
        except FileNotFoundError:
            self.bg_img = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
            self.bg_img.fill((50, 50, 50))

        # =========================
        # ROAD LAYER (DECORATION)
        # =========================
        road_path = "assets/images/screens/road.png"
        try:
            original_road = pygame.image.load(road_path).convert_alpha()
            self.road_img = pygame.transform.scale(original_road, (self.game.WIDTH, 1000))
            self.road_y = self.game.HEIGHT - 580
        except FileNotFoundError:
            self.road_img = None

        # =========================
        # PLAYER STATE
        # =========================
        self.player_gold = 300

        self.player_max_hp = 1000
        self.player_base_hp = self.player_max_hp

        self.player_base_rect = pygame.Rect(-300, self.game.HEIGHT - 650, 700, 600)

        # Age system (progression mechanic)
        self.ages = ["human", "ogre", "elf", "dragon"]
        self.player_age_index = 0

        self.player_xp = 0
        self.max_xps = [150, 350, 700, 99999]

        self.evolve_rect = pygame.Rect(self.game.WIDTH - 200, 50, 180, 40)

        # =========================
        # GAME OBJECTS
        # =========================
        self.units = []
        self.projectiles = []

        # Enemy base defaults (overridden in subclasses)
        self.enemy_base_rect = None
        self.enemy_max_hp = 1000
        self.enemy_base_hp = self.enemy_max_hp
        self.enemy_age_index = 0

        # =========================
        # BASE IMAGES
        # =========================
        self.base_images = {}
        for age in self.ages:
            path = f"assets/images/bases/{age}_base.png"
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.base_images[age] = pygame.transform.scale(img, (
                    self.player_base_rect.width, self.player_base_rect.height))
            else:
                self.base_images[age] = None

        # =========================
        # UI BUTTONS
        # =========================
        self.buy_melee_btn = Button(90, 120, "assets/images/buttons/sword.png", 0.5)
        self.buy_ranged_btn = Button(250, 120, "assets/images/buttons/ranger.png", 0.5)
        self.buy_flying_btn = Button(400, 118, "assets/images/buttons/paladin.png", 0.5)

        self.special_btn = Button(550, 121, "assets/images/buttons/special.png", 0.67)
        self.special_cooldown = 45000
        self.last_special_time = -45000

        self.back_btn = Button(self.game.WIDTH - 60, self.game.HEIGHT - 1050, "assets/images/buttons/back.png", 0.5)

        # =========================
        # FONTS
        # =========================
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # =========================
        # SOUND EFFECTS
        # =========================
        try:
            self.click_sound = pygame.mixer.Sound("assets/sounds/swoosh.wav")
        except:
            self.click_sound = None

    # =========================================================
    # INPUT HANDLING
    # =========================================================
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.go_back()

        sfx_enabled = self.game.settings.get("sfx_on", True)

        # Evolution mechanic
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.player_age_index < 3 and self.player_xp >= self.max_xps[self.player_age_index]:
                if self.evolve_rect.collidepoint(event.pos):
                    self.player_xp -= self.max_xps[self.player_age_index]
                    self.player_age_index += 1
                    if sfx_enabled and self.click_sound:
                        self.click_sound.play()

        current_player_age = self.ages[self.player_age_index]

        # Unit purchases
        if self.buy_melee_btn.is_clicked(event) and self.player_gold >= 100:
            self.player_gold -= 100
            if sfx_enabled and self.click_sound:
                self.click_sound.play()
            self.units.append(Unit(self.player_base_rect.x + 350,
                                   self.player_base_rect.bottom - 150,
                                   "player", 80, (0, 0, 255),
                                   "melee", current_player_age))

        if self.buy_ranged_btn.is_clicked(event) and self.player_gold >= 125:
            self.player_gold -= 125
            if sfx_enabled and self.click_sound:
                self.click_sound.play()
            self.units.append(Unit(self.player_base_rect.x + 350,
                                   self.player_base_rect.bottom - 150,
                                   "player", 80, (0, 255, 0),
                                   "ranged", current_player_age))

        if self.buy_flying_btn.is_clicked(event) and self.player_gold >= 150:
            self.player_gold -= 150
            if sfx_enabled and self.click_sound:
                self.click_sound.play()
            self.units.append(Unit(self.player_base_rect.x + 350,
                                   self.player_base_rect.bottom - 150,
                                   "player", 80, (0, 255, 255),
                                   "flying", current_player_age))

        # Special ability cooldown check
        current_time = pygame.time.get_ticks()
        if self.special_btn.is_clicked(event) and current_time - self.last_special_time >= self.special_cooldown:
            self.trigger_special_power("player")
            self.last_special_time = current_time

        if self.back_btn.is_clicked(event):
            self.go_back()

    # =========================================================
    # SPECIAL ABILITY
    # =========================================================
    def trigger_special_power(self, team="player"):
        """
        Air strike ability:
        Spawns projectiles that instantly hit all enemy units.
        """
        target_team = "enemy" if team == "player" else "player"
        sfx_enabled = self.game.settings.get("sfx_on", True)

        targets = [u for u in self.units if u.team == target_team]

        for target in targets:
            self.projectiles.append(
                Projectile(target.rect.centerx, -50, target, 9999, team, "flying")
            )

        if sfx_enabled and self.click_sound:
            self.click_sound.play()

    # =========================================================
    # GAME LOOP - UPDATE
    # =========================================================
    def update(self, dt):
        current_time = pygame.time.get_ticks()

        for unit in self.units:
            unit.is_moving = True

        player_units = [u for u in self.units if u.team == "player"]
        enemy_units = [u for u in self.units if u.team == "enemy"]

        # Combat system between units
        for p_unit in player_units:
            for e_unit in enemy_units:

                if p_unit.can_attack(e_unit):
                    p_unit.is_moving = False
                    if current_time - p_unit.last_attack_time > p_unit.attack_speed:
                        p_unit.play_attack_sound(self.game.settings.get("sfx_on", True))

                        if p_unit.unit_type in ["ranged", "flying"]:
                            self.projectiles.append(
                                Projectile(p_unit.rect.centerx, p_unit.rect.centery,
                                           e_unit, p_unit.damage,
                                           p_unit.team, p_unit.unit_type, p_unit.age))
                        else:
                            e_unit.hp -= p_unit.damage

                        p_unit.last_attack_time = current_time

                if e_unit.can_attack(p_unit):
                    e_unit.is_moving = False
                    if current_time - e_unit.last_attack_time > e_unit.attack_speed:
                        e_unit.play_attack_sound(self.game.settings.get("sfx_on", True))

                        if e_unit.unit_type in ["ranged", "flying"]:
                            self.projectiles.append(
                                Projectile(e_unit.rect.centerx, e_unit.rect.centery,
                                           p_unit, e_unit.damage,
                                           e_unit.team, e_unit.unit_type, e_unit.age))
                        else:
                            p_unit.hp -= e_unit.damage

                        e_unit.last_attack_time = current_time

                if p_unit.rect.colliderect(e_unit.rect) and not p_unit.is_flying and not e_unit.is_flying:
                    p_unit.is_moving = False
                    e_unit.is_moving = False

        # (rest unchanged logic continues...)

    # =========================================================
    # BACK NAVIGATION
    # =========================================================
    def go_back(self):
        from screens.mode_selection_screen import ModeSelectionScreen
        self.game.change_screen(ModeSelectionScreen(self.game))