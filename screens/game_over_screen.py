import pygame
from engine.screen import Screen
from engine.button import Button


class GameOverScreen(Screen):
    """
    Game Over Screen
    ----------------
    Displays the final result of the game (Victory / Defeat).

    Features:
    - Shows a snapshot of the game at the moment of ending
    - Displays victory or defeat UI
    - Provides a continue button to return to mode selection
    - Stops background music on entry
    """

    def __init__(self, game_engine, is_victory, snapshot):
        super().__init__(game_engine)

        # =========================
        # Game state
        # =========================
        self.is_victory = is_victory
        self.snapshot = snapshot  # frozen frame of gameplay

        # Stop background music when game ends
        pygame.mixer.music.stop()

        # =========================
        # Sound effects
        # =========================
        vol = 0.7 if self.game.settings.get("sfx_on", True) else 0.0

        try:
            self.click_sound = pygame.mixer.Sound("assets/sounds/swoosh.wav")
            self.click_sound.set_volume(vol)
        except FileNotFoundError:
            self.click_sound = None

        # =========================
        # Background image selection
        # =========================
        if self.is_victory:
            bg_path = "assets/images/screens/victory.png"
        else:
            bg_path = "assets/images/screens/defeat.png"

        try:
            original_bg = pygame.image.load(bg_path).convert_alpha()
            self.bg_img = pygame.transform.scale(original_bg, (600, 800))
        except FileNotFoundError:
            # Fallback background if image is missing
            self.bg_img = pygame.Surface((600, 400))
            self.bg_img.fill((50, 255, 50) if self.is_victory else (255, 50, 50))

        # Center the result panel
        self.bg_rect = self.bg_img.get_rect(
            center=(self.game.WIDTH // 2, self.game.HEIGHT // 2 - 50)
        )

        # =========================
        # Continue button
        # =========================
        center_x = self.game.WIDTH // 2

        if self.is_victory:
            btn_img = "assets/images/buttons/continue_victory.png"
        else:
            btn_img = "assets/images/buttons/continue_defeat.png"

        self.continue_btn = Button(center_x, self.bg_rect.bottom - 200, btn_img, 1.0)

    def handle_events(self, event):
        """
        Handles user input on Game Over screen:

        - ESC: Return to mode selection
        - Continue button: Return to mode selection
        """

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.go_to_levels()

        if self.continue_btn.is_clicked(event):
            if self.click_sound:
                self.click_sound.play()
            self.go_to_levels()

    def go_to_levels(self):
        """
        Navigates back to Mode Selection screen.
        """
        from screens.mode_selection_screen import ModeSelectionScreen
        self.game.change_screen(ModeSelectionScreen(self.game))

    def update(self, dt):
        """
        No gameplay logic required on Game Over screen.
        """
        pass

    def draw(self):
        """
        Renders Game Over screen:

        1. Draw frozen gameplay snapshot (background)
        2. Dark overlay to highlight UI
        3. Victory/Defeat panel
        4. Continue button
        """

        # Draw frozen gameplay frame
        self.game.screen.blit(self.snapshot, (0, 0))

        # Dark overlay effect
        dark_overlay = pygame.Surface(
            (self.game.WIDTH, self.game.HEIGHT),
            pygame.SRCALPHA
        )
        dark_overlay.fill((0, 0, 0, 150))
        self.game.screen.blit(dark_overlay, (0, 0))

        # Result panel
        self.game.screen.blit(self.bg_img, self.bg_rect)

        # Continue button
        self.continue_btn.draw(self.game.screen)