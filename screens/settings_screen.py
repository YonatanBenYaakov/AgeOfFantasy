import pygame
from engine.screen import Screen
from engine.button import Button


class SettingsScreen(Screen):
    """
    Settings screen for the game.

    This screen allows the player to:
    - Toggle music on/off
    - Toggle sound effects (SFX) on/off
    - Change difficulty (easy / normal / hard)
    - Return to the main menu

    It directly modifies the shared game_engine.settings dictionary,
    which is used across all game screens.
    """

    def __init__(self, game_engine):
        super().__init__(game_engine)

        # Load UI sounds for feedback
        self.beep_sound = pygame.mixer.Sound("assets/sounds/beep.wav")
        self.woosh_sound = pygame.mixer.Sound("assets/sounds/swoosh.wav")

        # Load and scale background image
        original_img = pygame.image.load("assets/images/screens/settings_board.png")
        self.board_img = pygame.transform.scale(original_img, (self.game.WIDTH, self.game.HEIGHT))
        self.board_rect = self.board_img.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT // 2))

        # Button layout positions
        btn_x = self.game.WIDTH // 2 + 150
        music_y = self.game.HEIGHT // 2 - 120
        sfx_y = self.game.HEIGHT // 2 - 20
        diff_y = self.game.HEIGHT // 2 + 80
        ok_y = self.game.HEIGHT // 2 + 200

        # Music toggle buttons (on/off states)
        self.music_on_btn = Button(btn_x, music_y - 20, "assets/images/buttons/on.png", 0.3)
        self.music_off_btn = Button(btn_x, music_y - 20, "assets/images/buttons/off.png", 0.3)

        # SFX toggle buttons (on/off states)
        self.sfx_on_btn = Button(btn_x, sfx_y - 20, "assets/images/buttons/on.png", 0.3)
        self.sfx_off_btn = Button(btn_x, sfx_y - 20, "assets/images/buttons/off.png", 0.3)

        # Difficulty selection buttons
        self.diff_easy_btn = Button(btn_x, diff_y - 20, "assets/images/buttons/easy.png", 0.24)
        self.diff_normal_btn = Button(btn_x, diff_y - 20, "assets/images/buttons/normal.png", 0.3)
        self.diff_hard_btn = Button(btn_x, diff_y - 20, "assets/images/buttons/hard.png", 0.24)

        # Confirm / exit button
        self.ok_btn = Button(self.game.WIDTH // 2, ok_y, "assets/images/buttons/ok.png", 1.0)

        # Apply initial sound settings
        self.update_sfx_volumes()

    def update_sfx_volumes(self):
        """
        Updates SFX volume based on current settings.

        If SFX is disabled, volume is set to 0.
        Otherwise, default volume levels are applied.
        """
        vol_beep = 0.5 if self.game.settings["sfx_on"] else 0.0
        vol_woosh = 0.7 if self.game.settings["sfx_on"] else 0.0

        self.beep_sound.set_volume(vol_beep)
        self.woosh_sound.set_volume(vol_woosh)

    def handle_events(self, event):
        """
        Handles all user input events (mouse clicks, key presses).

        Controls:
        - ESC: return to main menu
        - Toggle music on/off
        - Toggle SFX on/off
        - Cycle difficulty settings
        - OK button returns to menu
        """

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.woosh_sound.play()
            from screens.menu_screen import MenuScreen
            self.game.change_screen(MenuScreen(self.game))

        # -------------------------
        # Music toggle logic
        # -------------------------
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

        # -------------------------
        # SFX toggle logic
        # -------------------------
        if self.game.settings["sfx_on"]:
            if self.sfx_on_btn.is_clicked(event):
                self.game.settings["sfx_on"] = False
                self.update_sfx_volumes()
        else:
            if self.sfx_off_btn.is_clicked(event):
                self.game.settings["sfx_on"] = True
                self.update_sfx_volumes()
                self.beep_sound.play()

        # -------------------------
        # Difficulty cycling logic
        # (each click moves to next state)
        # -------------------------
        if self.game.settings["difficulty"] == "easy" and self.diff_easy_btn.is_clicked(event):
            self.game.settings["difficulty"] = "normal"
            self.beep_sound.play()

        elif self.game.settings["difficulty"] == "normal" and self.diff_normal_btn.is_clicked(event):
            self.game.settings["difficulty"] = "hard"
            self.beep_sound.play()

        elif self.game.settings["difficulty"] == "hard" and self.diff_hard_btn.is_clicked(event):
            self.game.settings["difficulty"] = "easy"
            self.beep_sound.play()

        # Return to menu via OK button
        if self.ok_btn.is_clicked(event):
            self.woosh_sound.play()
            from screens.menu_screen import MenuScreen
            self.game.change_screen(MenuScreen(self.game))

    def draw(self):
        """
        Renders the settings screen UI including:
        - Background board
        - Toggle buttons
        - Difficulty selection
        - OK button
        """

        self.game.screen.fill((20, 20, 20))
        self.game.screen.blit(self.board_img, self.board_rect)

        # Music button display state
        if self.game.settings["music_on"]:
            self.music_on_btn.draw(self.game.screen)
        else:
            self.music_off_btn.draw(self.game.screen)

        # SFX button display state
        if self.game.settings["sfx_on"]:
            self.sfx_on_btn.draw(self.game.screen)
        else:
            self.sfx_off_btn.draw(self.game.screen)

        # Difficulty button display state
        diff = self.game.settings["difficulty"]
        if diff == "easy":
            self.diff_easy_btn.draw(self.game.screen)
        elif diff == "normal":
            self.diff_normal_btn.draw(self.game.screen)
        elif diff == "hard":
            self.diff_hard_btn.draw(self.game.screen)

        # Confirm button
        self.ok_btn.draw(self.game.screen)

    def return_to_menu(self):
        """
        Safely returns the player to the main menu screen.
        Uses local import to avoid circular dependency issues.
        """
        from screens.menu_screen import MenuScreen
        self.game.current_screen = MenuScreen(self.game)