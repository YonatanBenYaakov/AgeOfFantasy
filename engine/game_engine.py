import pygame
import sys


class GameEngine:
    """
    Core game engine responsible for:
    - Initializing pygame
    - Managing the main game loop
    - Handling screen switching
    - Managing resolution scaling
    - Global settings (audio, difficulty, etc.)
    """

    def __init__(self, title="Age of Fantasy"):
        """
        Initialize the game engine and pygame systems.

        Args:
            title (str): Window title of the game.
        """

        # Initialize pygame core systems
        pygame.init()
        pygame.mixer.init()

        # =========================
        # Fullscreen window setup
        # =========================

        # Create fullscreen window (native monitor resolution)
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        # Actual screen resolution of the monitor
        self.WINDOW_WIDTH = self.window.get_width()
        self.WINDOW_HEIGHT = self.window.get_height()

        # Internal fixed resolution (game renders here)
        self.WIDTH = 1920
        self.HEIGHT = 1080

        # Internal rendering surface (logical canvas)
        self.screen = pygame.Surface((self.WIDTH, self.HEIGHT))

        pygame.display.set_caption(title)

        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = None

        # Global game settings (shared across screens)
        self.settings = {
            "music_on": True,
            "sfx_on": True,
            "difficulty": "normal"
        }

    def apply_settings(self):
        """
        Apply global audio settings (music volume control).
        Called whenever settings are updated.
        """
        if self.settings["music_on"]:
            pygame.mixer.music.set_volume(0.5)
        else:
            pygame.mixer.music.set_volume(0.0)

    def run(self, starting_screen):
        """
        Main game loop.

        Args:
            starting_screen (Screen): First screen to display.
        """
        self.current_screen = starting_screen

        while self.running:
            # Delta time (frame-independent movement)
            dt = self.clock.tick(60) / 1000.0

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()

                # =========================================
                # Mouse coordinate scaling (fullscreen fix)
                # =========================================
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):

                    ratio_x = self.WIDTH / self.WINDOW_WIDTH
                    ratio_y = self.HEIGHT / self.WINDOW_HEIGHT

                    # Transform mouse position to internal resolution space
                    event.__dict__['pos'] = (
                        int(event.pos[0] * ratio_x),
                        int(event.pos[1] * ratio_y)
                    )

                    # Transform relative mouse movement
                    if event.type == pygame.MOUSEMOTION:
                        event.__dict__['rel'] = (
                            int(event.rel[0] * ratio_x),
                            int(event.rel[1] * ratio_y)
                        )

                # Forward event to current screen
                if self.current_screen:
                    self.current_screen.handle_events(event)

            # Update logic
            if self.current_screen:
                self.current_screen.update(dt)

            # =========================
            # Rendering pipeline
            # =========================

            self.screen.fill((0, 0, 0))

            if self.current_screen:
                self.current_screen.draw()

            # Scale internal surface to actual screen size
            scaled_surface = pygame.transform.smoothscale(
                self.screen,
                (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            )

            self.window.blit(scaled_surface, (0, 0))
            pygame.display.flip()

    def change_screen(self, new_screen):
        """
        Switch between game screens.

        Args:
            new_screen (Screen): The new screen to activate.
        """
        if self.current_screen:
            self.current_screen.close()

        self.current_screen = new_screen

    def quit(self):
        """
        Cleanly exit the game and shut down pygame.
        """
        self.running = False

        if self.current_screen:
            self.current_screen.close()

        pygame.quit()
        sys.exit()