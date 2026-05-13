class Screen:
    """
    Base class for all game screens.

    This class defines the common interface that every screen in the game must implement,
    such as menu screens, gameplay screens, settings screens, etc.

    Each screen is responsible for handling its own:
    - events (input)
    - updates (game logic)
    - rendering (drawing)
    - cleanup when exiting
    """

    def __init__(self, game_engine):
        """
        Initialize the screen.

        Args:
            game_engine: Reference to the main game engine instance,
                         used to access global game state and utilities.
        """
        self.game = game_engine

    def handle_events(self, event):
        """
        Handle input events (keyboard, mouse, etc.).

        This method is called once per event in the main loop.
        Should be overridden by child classes.
        """
        pass

    def update(self, dt):
        """
        Update game logic for this screen.

        Args:
            dt (float): Delta time since last frame (for frame-independent movement/logic).
        """
        pass

    def draw(self):
        """
        Render the screen.

        This method should draw everything visible on this screen.
        Should be overridden by child classes.
        """
        pass

    def close(self):
        """
        Cleanup resources when leaving the screen.

        Examples:
        - stopping music
        - releasing video/audio resources
        - saving state
        """
        pass