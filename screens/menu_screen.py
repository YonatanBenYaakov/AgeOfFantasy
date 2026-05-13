import pygame
import cv2
from engine.screen import Screen
from engine.button import Button
from screens.settings_screen import SettingsScreen


class MenuScreen(Screen):
    """
    Main Menu Screen
    ----------------
    This is the first screen of the game.

    Responsibilities:
    - Play looping background video (OpenCV)
    - Play background music
    - Handle navigation to:
        * Mode Selection
        * Settings
        * Exit game
    """

    def __init__(self, game_engine):
        super().__init__(game_engine)

        # =========================
        # Background video setup
        # =========================
        self.video = cv2.VideoCapture("assets/videos/bg1loop.mp4")
        self.current_frame = None

        self.video_timer = 0
        self.video_speed = 2  # controls frame skipping speed

        # =========================
        # Background music setup
        # =========================
        pygame.mixer.music.load("assets/music/menu_theme_2.mp3")

        # Apply global volume settings from engine
        self.game.apply_settings()
        pygame.mixer.music.play(-1)

        # =========================
        # Sound effects
        # =========================
        self.click_sound = pygame.mixer.Sound("assets/sounds/swoosh.wav")

        vol = 0.7 if self.game.settings["sfx_on"] else 0.0
        self.click_sound.set_volume(vol)

        # =========================
        # UI Buttons
        # =========================
        center_x = self.game.WIDTH // 2

        self.start_button = Button(center_x, 550, "assets/images/buttons/start_game.png", 0.8)
        self.settings_button = Button(center_x, 750, "assets/images/buttons/settings.png", 0.8)
        self.exit_button = Button(center_x, 950, "assets/images/buttons/exit.png", 0.8)

    def handle_events(self, event):
        """
        Handles user input in the main menu:

        - ESC: Quit game
        - Start: Go to mode selection
        - Settings: Open settings screen
        - Exit: Quit game
        """

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

        # =========================
        # Start game flow
        # =========================
        if self.start_button.is_clicked(event):
            self.click_sound.play()

            from screens.mode_selection_screen import ModeSelectionScreen
            self.game.change_screen(ModeSelectionScreen(self.game))

        # =========================
        # Settings flow
        # =========================
        if self.settings_button.is_clicked(event):
            self.click_sound.play()
            self.game.change_screen(SettingsScreen(self.game))

        # =========================
        # Exit game
        # =========================
        if self.exit_button.is_clicked(event):
            self.click_sound.play()
            self.game.quit()

    def update(self, dt):
        """
        Updates background video frame by frame.

        OpenCV reads video frames and converts them into
        a Pygame surface for rendering.
        """

        self.video_timer += 1

        # Control video playback speed
        if self.video_timer >= self.video_speed:
            self.video_timer = 0

            success, frame = self.video.read()

            # Loop video when it ends
            if not success:
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                success, frame = self.video.read()

            if success:
                frame = cv2.resize(frame, (self.game.WIDTH, self.game.HEIGHT))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                self.current_frame = pygame.image.frombuffer(
                    frame.tobytes(),
                    (self.game.WIDTH, self.game.HEIGHT),
                    "RGB"
                )

    def draw(self):
        """
        Renders menu screen:
        - Background video
        - UI buttons on top
        """

        if self.current_frame:
            self.game.screen.blit(self.current_frame, (0, 0))

        self.start_button.draw(self.game.screen)
        self.settings_button.draw(self.game.screen)
        self.exit_button.draw(self.game.screen)

    def close(self):
        """
        Releases video resources when leaving the screen.
        Ensures no memory leaks from OpenCV.
        """
        self.video.release()