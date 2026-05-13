from engine.game_engine import GameEngine
from screens.menu_screen import MenuScreen


def main():
    """
    Entry point of the game.

    Responsibilities:
    - Initializes the core game engine
    - Loads the initial menu screen
    - Starts the main game loop
    """

    # =========================
    # Engine Initialization
    # =========================
    # Creates the main game engine instance
    # This handles rendering, updates, input, and screen switching
    engine = GameEngine()

    # =========================
    # Initial Screen Setup
    # =========================
    # Creates the main menu screen and attaches it to the engine
    # This is the first screen the player sees when launching the game
    menu = MenuScreen(engine)

    # =========================
    # Game Start
    # =========================
    # Starts the main loop of the game using the menu as the entry screen
    engine.run(menu)


# =========================
# Program Entry Point
# =========================
# Ensures that the game only starts when this file is executed directly
if __name__ == "__main__":
    main()