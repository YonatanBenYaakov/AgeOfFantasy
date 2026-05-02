import pygame
from engine.screen import Screen
from engine.button import Button


class GameOverScreen(Screen):
    def __init__(self, game_engine, is_victory, snapshot):
        super().__init__(game_engine)
        self.is_victory = is_victory
        self.snapshot = snapshot

        pygame.mixer.music.stop()

        vol = 0.7 if self.game.settings.get("sfx_on", True) else 0.0
        try:
            self.click_sound = pygame.mixer.Sound("assets/sounds/swoosh.wav")
            self.click_sound.set_volume(vol)
        except FileNotFoundError:
            self.click_sound = None

        if self.is_victory:
            bg_path = "assets/images/screens/victory.png"
        else:
            bg_path = "assets/images/screens/defeat.png"

        try:
            original_bg = pygame.image.load(bg_path).convert_alpha()
            self.bg_img = pygame.transform.scale(original_bg, (600, 800))
        except FileNotFoundError:
            self.bg_img = pygame.Surface((600, 400))
            self.bg_img.fill((50, 255, 50) if self.is_victory else (255, 50, 50))

        self.bg_rect = self.bg_img.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT // 2 - 50))

        center_x = self.game.WIDTH // 2
        btn_y = self.bg_rect.bottom + 50

        if self.is_victory:
            btn_img = "assets/images/buttons/continue_victory.png"
        else:
            btn_img = "assets/images/buttons/continue_defeat.png"

        self.continue_btn = Button(center_x, btn_y - 200, btn_img, 1.0)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.go_to_levels()

        if self.continue_btn.is_clicked(event):
            if self.click_sound: self.click_sound.play()
            self.go_to_levels()

    def go_to_levels(self):
        from screens.mode_selection_screen import ModeSelectionScreen
        self.game.change_screen(ModeSelectionScreen(self.game))

    def update(self,dt):
        pass

    def draw(self):
        self.game.screen.blit(self.snapshot, (0, 0))

        dark_overlay = pygame.Surface((self.game.WIDTH, self.game.HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 150))
        self.game.screen.blit(dark_overlay, (0, 0))

        self.game.screen.blit(self.bg_img, self.bg_rect)
        self.continue_btn.draw(self.game.screen)