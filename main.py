from engine.game_engine import GameEngine
from screens.menu_screen import MenuScreen


def main():
    # יצירת המנוע (בגודל 1280x720, אפשר לשנות)
    engine = GameEngine()

    # יצירת מסך הפתיחה
    menu = MenuScreen(engine)

    # הרצת המשחק על מסך הפתיחה
    engine.run(menu)


if __name__ == "__main__":
    main()