import pygame
from engine.screen import Screen
from engine.button import Button
# מייבאים את המסכים החדשים שיצרנו
from screens.vs_bot_screen import VsBotScreen
from screens.pvp_screen import PvPScreen
from screens.survival_screen import SurvivalScreen

class ModeSelectionScreen(Screen):
    def __init__(self, game_engine):
        super().__init__(game_engine)

        # טעינת תמונת הרקע
        original_bg = pygame.image.load("assets/images/screens/mode_selection_bg.png")
        self.bg_img = pygame.transform.scale(original_bg, (self.game.WIDTH, self.game.HEIGHT))

        # --- טעינת הצלילים ---
        vol = 0.7 if self.game.settings.get("sfx_on", True) else 0.0

        self.click_sound = pygame.mixer.Sound("assets/sounds/swoosh.wav")
        self.click_sound.set_volume(vol)

        self.ding_sound = pygame.mixer.Sound("assets/sounds/ting.wav")
        self.ding_sound.set_volume(vol)

        # משתנה לשמירת המוד הנבחר
        self.selected_mode = None

        # חישוב מיקומים
        center_y = self.game.HEIGHT // 2
        left_x = self.game.WIDTH // 4
        mid_x = self.game.WIDTH // 2
        right_x = 3 * self.game.WIDTH // 4

        # יצירת הלחצנים של המודים
        self.classic_btn = Button(left_x - 50, center_y, "assets/images/buttons/btn_classic.png", 1.5)
        self.pvp_btn = Button(mid_x, center_y, "assets/images/buttons/btn_pvp.png", 1.5)
        self.survival_btn = Button(right_x + 50, center_y, "assets/images/buttons/btn_survival.png", 1.5)

        # יצירת כפתור אישור וחזרה
        confirm_y = self.game.HEIGHT - 50
        self.confirm_btn = Button(mid_x, confirm_y, "assets/images/buttons/confirm.png", 1.0)
        self.back_btn = Button(150, confirm_y, "assets/images/buttons/back.png", 1.0)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.go_back()

        # --- בדיקת לחיצות על המודים ---
        if self.classic_btn.is_clicked(event):
            self.ding_sound.play()
            self.selected_mode = "classic"

        # הפעלנו את הלחצנים של שאר המודים!
        elif self.pvp_btn.is_clicked(event):
            self.ding_sound.play()
            self.selected_mode = "pvp"

        elif self.survival_btn.is_clicked(event):
            self.ding_sound.play()
            self.selected_mode = "survival"

        # --- אישור בחירה ---
        if self.confirm_btn.is_clicked(event):
            if self.selected_mode is not None:
                self.click_sound.play()
                print(f"Starting game in {self.selected_mode} mode!")

                # טעינת המחלקה הנכונה לפי המוד שנבחר
                if self.selected_mode == "classic":
                    self.game.change_screen(VsBotScreen(self.game))
                elif self.selected_mode == "pvp":
                    self.game.change_screen(PvPScreen(self.game))
                elif self.selected_mode == "survival":
                    self.game.change_screen(SurvivalScreen(self.game))
            else:
                print("Please select a mode first!")

        # --- חזור ---
        if self.back_btn.is_clicked(event):
            self.click_sound.play()
            self.go_back()

    def go_back(self):
        from screens.menu_screen import MenuScreen
        self.game.change_screen(MenuScreen(self.game))

    def update(self,dt):
        pass

    def draw_enlarged_button(self, btn):
        new_width = int(btn.rect.width * 1.1)
        new_height = int(btn.rect.height * 1.1)
        scaled_img = pygame.transform.smoothscale(btn.image, (new_width, new_height))
        scaled_rect = scaled_img.get_rect(center=btn.rect.center)
        self.game.screen.blit(scaled_img, scaled_rect)

    def draw(self):
        self.game.screen.blit(self.bg_img, (0, 0))

        if self.selected_mode != "classic":
            self.classic_btn.draw(self.game.screen)
        if self.selected_mode != "pvp":
            self.pvp_btn.draw(self.game.screen)
        if self.selected_mode != "survival":
            self.survival_btn.draw(self.game.screen)

        if self.selected_mode == "classic":
            self.draw_enlarged_button(self.classic_btn)
        elif self.selected_mode == "pvp":
            self.draw_enlarged_button(self.pvp_btn)
        elif self.selected_mode == "survival":
            self.draw_enlarged_button(self.survival_btn)

        self.confirm_btn.draw(self.game.screen)
        self.back_btn.draw(self.game.screen)