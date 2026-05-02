import pygame
from engine.screen import Screen
# שים לב לייבא את מחלקת הכפתור שלך מהמיקום הנכון שלה!
from engine.button import Button


class SettingsScreen(Screen):
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.beep_sound = pygame.mixer.Sound("assets/sounds/beep.wav")
        self.woosh_sound = pygame.mixer.Sound("assets/sounds/swoosh.wav")

        # טעינת רקע
        original_img = pygame.image.load("assets/images/screens/settings_board.png")
        self.board_img = pygame.transform.scale(original_img, (self.game.WIDTH, self.game.HEIGHT))
        self.board_rect = self.board_img.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT // 2))

        btn_x = self.game.WIDTH // 2 + 150
        music_y = self.game.HEIGHT // 2 - 120
        sfx_y = self.game.HEIGHT // 2 - 20
        diff_y = self.game.HEIGHT // 2 + 80
        ok_y = self.game.HEIGHT // 2 + 200

        # כפתורים
        self.music_on_btn = Button(btn_x, music_y - 20, "assets/images/buttons/on.png", 0.3)
        self.music_off_btn = Button(btn_x, music_y - 20, "assets/images/buttons/off.png", 0.3)
        self.sfx_on_btn = Button(btn_x, sfx_y - 20, "assets/images/buttons/on.png", 0.3)
        self.sfx_off_btn = Button(btn_x, sfx_y - 20, "assets/images/buttons/off.png", 0.3)

        self.diff_easy_btn = Button(btn_x, diff_y - 20, "assets/images/buttons/easy.png", 0.24)
        self.diff_normal_btn = Button(btn_x, diff_y - 20, "assets/images/buttons/normal.png", 0.3)
        self.diff_hard_btn = Button(btn_x, diff_y - 20, "assets/images/buttons/hard.png", 0.24)

        self.ok_btn = Button(self.game.WIDTH // 2, ok_y, "assets/images/buttons/ok.png", 1.0)

        # עדכון הווליום של האפקטים לפי המצב השמור
        self.update_sfx_volumes()

    def update_sfx_volumes(self):
        vol_beep = 0.5 if self.game.settings["sfx_on"] else 0.0
        vol_woosh = 0.7 if self.game.settings["sfx_on"] else 0.0
        self.beep_sound.set_volume(vol_beep)
        self.woosh_sound.set_volume(vol_woosh)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.woosh_sound.play()
            # חייבים לייבא את המסך לפני שמשתמשים בו!
            from screens.menu_screen import MenuScreen
            self.game.change_screen(MenuScreen(self.game))

        # --- מוזיקה ---
        if self.game.settings["music_on"]:
            if self.music_on_btn.is_clicked(event):
                self.game.settings["music_on"] = False
                self.game.apply_settings()
                self.beep_sound.play()
        else:
            if self.music_off_btn.is_clicked(event):
                self.game.settings["music_on"] = True
                self.game.apply_settings()
                self.beep_sound.play()

        # --- אפקטים (SFX) ---
        if self.game.settings["sfx_on"]:
            if self.sfx_on_btn.is_clicked(event):
                self.game.settings["sfx_on"] = False
                self.update_sfx_volumes()
        else:
            if self.sfx_off_btn.is_clicked(event):
                self.game.settings["sfx_on"] = True
                self.update_sfx_volumes()
                self.beep_sound.play()

        # --- קושי ---
        if self.game.settings["difficulty"] == "easy" and self.diff_easy_btn.is_clicked(event):
            self.game.settings["difficulty"] = "normal"
            self.beep_sound.play()
        elif self.game.settings["difficulty"] == "normal" and self.diff_normal_btn.is_clicked(event):
            self.game.settings["difficulty"] = "hard"
            self.beep_sound.play()
        elif self.game.settings["difficulty"] == "hard" and self.diff_hard_btn.is_clicked(event):
            self.game.settings["difficulty"] = "easy"
            self.beep_sound.play()

        if self.ok_btn.is_clicked(event):
            self.woosh_sound.play()
            from screens.menu_screen import MenuScreen
            self.game.change_screen(MenuScreen(self.game))

    def draw(self):
        self.game.screen.fill((20, 20, 20))
        self.game.screen.blit(self.board_img, self.board_rect)

        # מציירים לפי המצב ב-engine
        if self.game.settings["music_on"]:
            self.music_on_btn.draw(self.game.screen)
        else:
            self.music_off_btn.draw(self.game.screen)

        if self.game.settings["sfx_on"]:
            self.sfx_on_btn.draw(self.game.screen)
        else:
            self.sfx_off_btn.draw(self.game.screen)

        diff = self.game.settings["difficulty"]
        if diff == "easy":
            self.diff_easy_btn.draw(self.game.screen)
        elif diff == "normal":
            self.diff_normal_btn.draw(self.game.screen)
        elif diff == "hard":
            self.diff_hard_btn.draw(self.game.screen)

        self.ok_btn.draw(self.game.screen)
    def return_to_menu(self):
        # ייבוא פנימי כדי למנוע שגיאות (Circular Import)
        from screens.menu_screen import MenuScreen
        self.game.current_screen = MenuScreen(self.game)