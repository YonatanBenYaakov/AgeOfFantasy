import pygame
import cv2
from engine.screen import Screen
from engine.button import Button
from screens.settings_screen import SettingsScreen


class MenuScreen(Screen):
    def __init__(self, game_engine):
        super().__init__(game_engine)

        # טעינת הוידאו... (הקוד הקיים שלך)
        self.video = cv2.VideoCapture("assets/videos/bg1loop.mp4")
        self.current_frame = None

        self.video_timer = 0
        self.video_speed = 2

        # --- טעינת והפעלת מוזיקת רקע ---
        # שים לב לשנות את השם לשם של הקובץ שלך!

        # טוענים מוזיקה אבל מחילים את הווליום מה-engine!
        pygame.mixer.music.load("assets/music/menu_theme_2.mp3")
        self.game.apply_settings()  # <--- השורה החשובה!
        pygame.mixer.music.play(-1)

        self.click_sound = pygame.mixer.Sound("assets/sounds/swoosh.wav")
        # ווליום לאפקטים
        vol = 0.7 if self.game.settings["sfx_on"] else 0.0
        self.click_sound.set_volume(vol)

            # ... כפתורים ...

        center_x = self.game.WIDTH // 2

        self.start_button = Button(center_x, 550 , "assets/images/buttons/start_game.png", 0.8)
        self.settings_button = Button(center_x, 750, "assets/images/buttons/settings.png", 0.8)
        self.exit_button = Button(center_x, 950, "assets/images/buttons/exit.png", 0.8)
        # יצירת הכפתורים... (הקוד הקיים שלך)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

        if self.start_button.is_clicked(event):
            self.click_sound.play()
            from screens.mode_selection_screen import ModeSelectionScreen  # יבוא פנימי
            self.game.change_screen(ModeSelectionScreen(self.game))

        # בתוך handle_events של MenuScreen
        if self.settings_button.is_clicked(event):
            self.click_sound.play()
            print("Settings Clicked!")
            # במקום self.game.current_screen = ...
            # נשתמש בזה:
            self.game.change_screen(SettingsScreen(self.game))

        if self.exit_button.is_clicked(event):
            self.click_sound.play()  # השמעת צליל לחיצה
            print("Exit Clicked!")
            self.game.quit()

    # ... פונקציות update ו-draw נשארות אותו דבר ...

    def close(self):
        self.video.release()
        pygame.mixer.music.stop()  # עצירת המוזיקה כשיוצאים מהמסך

    def update(self,dt):
        # 1. מוסיפים 1 לטיימר בכל סיבוב של המשחק
        self.video_timer += 1

        # 2. רק אם הטיימר הגיע למהירות שהגדרנו, נטען פריים חדש מהווידאו
        if self.video_timer >= self.video_speed:
            self.video_timer = 0  # מאפסים את הטיימר לסיבוב הבא

            success, frame = self.video.read()
            if not success:
                # מתחיל את הוידאו מהתחלה כשהוא נגמר
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = self.video.read()

            if success:
                # המרת הפריים ל-Pygame
                frame = cv2.resize(frame, (self.game.WIDTH, self.game.HEIGHT))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame = pygame.image.frombuffer(
                    frame.tobytes(), (self.game.WIDTH, self.game.HEIGHT), "RGB"
                )

    def draw(self):
        # ציור הרקע
        if self.current_frame:
            self.game.screen.blit(self.current_frame, (0, 0))

        # ציור הכפתורים מעל הרקע
        self.start_button.draw(self.game.screen)
        self.settings_button.draw(self.game.screen)
        self.exit_button.draw(self.game.screen)

    def close(self):
        # שחרור משאבי הוידאו כשיוצאים מהמסך
        self.video.release()