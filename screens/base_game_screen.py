# -*- coding: utf-8 -*-
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
        return self.screen.player_base_hp if self.team == "player" else self.screen.enemy_base_hp

    @hp.setter
    def hp(self, value):
        if self.team == "player":
            self.screen.player_base_hp = value
        else:
            self.screen.enemy_base_hp = value


class BaseGameScreen(Screen):
    """
    Core gameplay class shared by all game modes.
    Handles rendering, updates, resources, and win/lose conditions.
    """
    def __init__(self, game_engine):
        super().__init__(game_engine)

        # --- טעינת והפעלת מוזיקת רקע למשחק ---
        music_path = "assets/music/game_music.mp3"
        if self.game.settings.get("music_on", True):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Could not load game music: {e}")

        # --- טעינת רקע המשחק ---
        bg_path = "assets/images/screens/human_arena.png"
        try:
            original_bg = pygame.image.load(bg_path)
            self.bg_img = pygame.transform.scale(original_bg, (self.game.WIDTH, self.game.HEIGHT))
        except FileNotFoundError:
            self.bg_img = pygame.Surface((self.game.WIDTH, self.game.HEIGHT))
            self.bg_img.fill((50, 50, 50))

        # --- טעינת תמונת הדרך ---
        road_path = "assets/images/screens/road.png"
        try:
            original_road = pygame.image.load(road_path).convert_alpha()
            self.road_img = pygame.transform.scale(original_road, (self.game.WIDTH, 1000))
            self.road_y = self.game.HEIGHT - 580
        except FileNotFoundError:
            self.road_img = None

        # --- משתני שחקן 1 ---
        self.player_gold = 300
        self.player_max_hp = 1000
        self.player_base_hp = self.player_max_hp
        self.player_base_rect = pygame.Rect(-300, self.game.HEIGHT - 650, 700, 600)

        self.ages = ["human", "ogre", "elf", "dragon"]
        self.player_age_index = 0
        self.player_xp = 0
        self.max_xps = [150, 350, 700, 99999]
        self.evolve_rect = pygame.Rect(self.game.WIDTH - 200, 50, 180, 40)

        # --- רשימות אובייקטים ---
        self.units = []
        self.projectiles = []

        # --- משתני אויב דיפולטיביים ---
        self.enemy_base_rect = None
        self.enemy_max_hp = 1000
        self.enemy_base_hp = self.enemy_max_hp
        self.enemy_age_index = 0

        # --- טעינת תמונות הבסיסים ---
        self.base_images = {}
        for age in self.ages:
            path = f"assets/images/bases/{age}_base.png"
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.base_images[age] = pygame.transform.scale(img, (self.player_base_rect.width, self.player_base_rect.height))
            else:
                self.base_images[age] = None

        # --- לחצני UI ---
        self.buy_melee_btn = Button(90, 120, "assets/images/buttons/sword.png", 0.5)
        self.buy_ranged_btn = Button(250, 120, "assets/images/buttons/ranger.png", 0.5)
        self.buy_flying_btn = Button(400, 118, "assets/images/buttons/paladin.png", 0.5)

        # --- כוח מיוחד ---
        self.special_btn = Button(550, 121, "assets/images/buttons/special.png", 0.67)
        self.special_cooldown = 45000
        self.last_special_time = -45000

        self.back_btn = Button(self.game.WIDTH - 60, self.game.HEIGHT - 1050, "assets/images/buttons/back.png", 0.5)

        # --- פונטים ואפקטים ---
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        try:
            self.click_sound = pygame.mixer.Sound("assets/sounds/swoosh.wav")
        except:
            self.click_sound = None

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.go_back()

        sfx_enabled = self.game.settings.get("sfx_on", True)

        # מנגנון התפתחות עידנים
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.player_age_index < 3 and self.player_xp >= self.max_xps[self.player_age_index]:
                if self.evolve_rect.collidepoint(event.pos):
                    self.player_xp -= self.max_xps[self.player_age_index]
                    self.player_age_index += 1
                    if sfx_enabled and self.click_sound:
                        self.click_sound.play()

        current_player_age = self.ages[self.player_age_index]

        # רכישת יחידות
        if self.buy_melee_btn.is_clicked(event) and self.player_gold >= 100:
            self.player_gold -= 100
            if sfx_enabled and self.click_sound:
                self.click_sound.play()
            self.units.append(Unit(self.player_base_rect.x + 350, self.player_base_rect.bottom - 150, "player", 80, (0, 0, 255), "melee", current_player_age))

        if self.buy_ranged_btn.is_clicked(event) and self.player_gold >= 125:
            self.player_gold -= 125
            if sfx_enabled and self.click_sound:
                self.click_sound.play()
            self.units.append(Unit(self.player_base_rect.x + 350, self.player_base_rect.bottom - 150, "player", 80, (0, 255, 0), "ranged", current_player_age))

        if self.buy_flying_btn.is_clicked(event) and self.player_gold >= 150:
            self.player_gold -= 150
            if sfx_enabled and self.click_sound:
                self.click_sound.play()
            self.units.append(Unit(self.player_base_rect.x + 350, self.player_base_rect.bottom - 150, "player", 80, (0, 255, 255), "flying", current_player_age))

        current_time = pygame.time.get_ticks()
        time_since_special = current_time - self.last_special_time

        if self.special_btn.is_clicked(event) and time_since_special >= self.special_cooldown:
            self.trigger_special_power("player")
            self.last_special_time = current_time

        if self.back_btn.is_clicked(event):
            self.go_back()

    def trigger_special_power(self, team="player"):
        target_team = "enemy" if team == "player" else "player"
        sfx_enabled = self.game.settings.get("sfx_on", True)

        targets = [u for u in self.units if u.team == target_team]
        for target in targets:
            self.projectiles.append(Projectile(target.rect.centerx, -50, target, 9999, team, "flying"))

        if sfx_enabled and self.click_sound:
            self.click_sound.play()

    def go_back(self):
        from screens.mode_selection_screen import ModeSelectionScreen
        self.game.change_screen(ModeSelectionScreen(self.game))

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        for unit in self.units:
            unit.is_moving = True

        player_units = [u for u in self.units if u.team == "player"]
        enemy_units = [u for u in self.units if u.team == "enemy"]

        # לוגיקת קרב בין חיילים
        for p_unit in player_units:
            for e_unit in enemy_units:
                if p_unit.can_attack(e_unit):
                    p_unit.is_moving = False
                    if current_time - p_unit.last_attack_time > p_unit.attack_speed:
                        p_unit.play_attack_sound(self.game.settings.get("sfx_on", True))
                        if p_unit.unit_type in ["ranged", "flying"]:
                            self.projectiles.append(Projectile(p_unit.rect.centerx, p_unit.rect.centery, e_unit, p_unit.damage, p_unit.team, p_unit.unit_type, p_unit.age))
                        else:
                            e_unit.hp -= p_unit.damage
                        p_unit.last_attack_time = current_time

                if e_unit.can_attack(p_unit):
                    e_unit.is_moving = False
                    if current_time - e_unit.last_attack_time > e_unit.attack_speed:
                        e_unit.play_attack_sound(self.game.settings.get("sfx_on", True))
                        if e_unit.unit_type in ["ranged", "flying"]:
                            self.projectiles.append(Projectile(e_unit.rect.centerx, e_unit.rect.centery, p_unit, e_unit.damage, e_unit.team, e_unit.unit_type, e_unit.age))
                        else:
                            p_unit.hp -= e_unit.damage
                        e_unit.last_attack_time = current_time

                if p_unit.rect.colliderect(e_unit.rect) and not p_unit.is_flying and not e_unit.is_flying:
                    p_unit.is_moving = False
                    e_unit.is_moving = False

        # פגיעה בבסיסים
        for unit in self.units:
            is_enemy_base = (unit.team == "player")
            target_base_rect = self.enemy_base_rect if is_enemy_base else self.player_base_rect

            if target_base_rect:
                stop_dist = 250 if unit.unit_type in ["ranged", "flying"] else 0
                if unit.team == "player":
                    reach_rect = pygame.Rect(target_base_rect.x - stop_dist, target_base_rect.y, target_base_rect.width + stop_dist, target_base_rect.height)
                else:
                    reach_rect = pygame.Rect(target_base_rect.x, target_base_rect.y, target_base_rect.width + stop_dist, target_base_rect.height)

                if unit.rect.colliderect(reach_rect):
                    unit.is_moving = False
                    if current_time - unit.last_attack_time > unit.attack_speed:
                        unit.play_attack_sound(self.game.settings.get("sfx_on", True))
                        if unit.unit_type in ["ranged", "flying"]:
                            target_team = "enemy" if is_enemy_base else "player"
                            dummy_base = BaseTarget(target_base_rect, target_team, self)
                            self.projectiles.append(Projectile(unit.rect.centerx, unit.rect.centery, dummy_base, unit.damage, unit.team, unit.unit_type, unit.age))
                        else:
                            if is_enemy_base:
                                self.enemy_base_hp -= unit.damage
                            else:
                                self.player_base_hp -= unit.damage
                        unit.last_attack_time = current_time

        # עדכון יחידות חיות
        alive_units = []
        for unit in self.units:
            if unit.hp > 0:
                unit.update(dt)
                alive_units.append(unit)
            elif unit.team == "enemy":
                self.player_gold += 125
                self.player_xp += 25
        self.units = alive_units

        # עדכון קליעים
        active_projectiles = []
        for proj in self.projectiles:
            proj.update(dt)
            if proj.active:
                active_projectiles.append(proj)
        self.projectiles = active_projectiles

        # בדיקת סיום משחק
        if self.player_base_hp <= 0:
            snapshot = self.game.screen.copy()
            self.game.change_screen(GameOverScreen(self.game, is_victory=False, snapshot=snapshot))
        elif self.enemy_base_hp <= 0 and self.enemy_base_rect is not None:
            snapshot = self.game.screen.copy()
            self.game.change_screen(GameOverScreen(self.game, is_victory=True, snapshot=snapshot))

    def draw(self):
        # 1. ציור הרקע
        if self.bg_img:
            self.game.screen.blit(self.bg_img, (0, 0))

        # 2. ציור הדרך
        if self.road_img:
            self.game.screen.blit(self.road_img, (0, self.road_y))

        # 3. ציור בסיס השחקן
        player_base_img = self.base_images.get(self.ages[self.player_age_index])
        if player_base_img:
            self.game.screen.blit(player_base_img, self.player_base_rect)

        # 4. מד חיים (Health Bar) לשחקן
        hp_bar_width = 200
        hp_bar_height = 20
        hp_bar_x = self.player_base_rect.x + 350
        hp_bar_y = self.player_base_rect.y - 30

        p_hp_ratio = max(0, self.player_base_hp / self.player_max_hp)
        pygame.draw.rect(self.game.screen, (255, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        pygame.draw.rect(self.game.screen, (0, 255, 0), (hp_bar_x, hp_bar_y, hp_bar_width * p_hp_ratio, hp_bar_height))
        pygame.draw.rect(self.game.screen, (0, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)

        # 5. ציור חיילים וקליעים
        for unit in self.units:
            unit.draw(self.game.screen)
        for proj in self.projectiles:
            proj.draw(self.game.screen)

        # 6. ציור ממשק משתמש (UI) וכפתורים
        self.buy_melee_btn.draw(self.game.screen)
        self.buy_ranged_btn.draw(self.game.screen)
        self.buy_flying_btn.draw(self.game.screen)
        self.back_btn.draw(self.game.screen)

        # כפתור ספיישל עם שכבת קולדאון
        self.special_btn.draw(self.game.screen)
        current_time = pygame.time.get_ticks()
        time_since_special = current_time - self.last_special_time

        if time_since_special < self.special_cooldown:
            overlay = pygame.Surface((self.special_btn.rect.width, self.special_btn.rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.game.screen.blit(overlay, self.special_btn.rect.topleft)

            seconds_left = (self.special_cooldown - time_since_special) // 1000
            cd_text = self.font.render(str(seconds_left), True, (255, 255, 255))
            text_rect = cd_text.get_rect(center=self.special_btn.rect.center)
            self.game.screen.blit(cd_text, text_rect)

        # הצגת נתוני זהב
        gold_text = self.font.render(f"Gold: {self.player_gold}", True, (255, 215, 0))
        self.game.screen.blit(gold_text, (20, 10))

        # מד ניסיון (XP Bar)
        current_max_xp = self.max_xps[self.player_age_index]
        if self.player_age_index < 3:
            xp_bar_width = 200
            xp_bar_height = 25
            xp_bar_x = self.game.WIDTH - 350
            xp_bar_y = 10

            xp_ratio = min(1.0, max(0, self.player_xp / current_max_xp))
            pygame.draw.rect(self.game.screen, (50, 50, 50), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
            pygame.draw.rect(self.game.screen, (0, 200, 255), (xp_bar_x, xp_bar_y, xp_bar_width * xp_ratio, xp_bar_height))
            pygame.draw.rect(self.game.screen, (255, 255, 255), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), 2)

            xp_label = self.small_font.render("XP", True, (255, 255, 255))
            self.game.screen.blit(xp_label, (xp_bar_x - 30, xp_bar_y + 4))

            if self.player_xp >= current_max_xp:
                pygame.draw.rect(self.game.screen, (255, 215, 0), self.evolve_rect)
                pygame.draw.rect(self.game.screen, (0, 0, 0), self.evolve_rect, 3)
                evolve_txt = self.font.render("EVOLVE!", True, (0, 0, 0))
                self.game.screen.blit(evolve_txt, (self.evolve_rect.x + 10, self.evolve_rect.y + 10))
        else:
            xp_text = self.font.render("AGE: MAX (DRAGONS)", True, (0, 255, 255))
            self.game.screen.blit(xp_text, (self.game.WIDTH - 300, 10))