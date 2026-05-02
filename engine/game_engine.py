import pygame
import sys


class GameEngine:
    def __init__(self, title="Age of Fantasy"):
        # 1. קודם כל מפעילים את הליבה של pygame
        pygame.init()
        # 2. אחר כך מפעילים את הסאונד
        pygame.mixer.init()

        # --- הגדרות חלון ורזולוציה מקצועיות (מסך מלא מתוח) ---

        # יצירת מסך מלא באופן אוטומטי על כל הגודל של המחשב הנוכחי
        self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        # אנחנו שולפים את המידות האמיתיות של המסך ש-pygame מצא
        self.WINDOW_WIDTH = self.window.get_width()
        self.WINDOW_HEIGHT = self.window.get_height()

        # הרזולוציה הלוגית שעליה בנוי המשחק (לא משתנה אף פעם!)
        self.WIDTH = 1920
        self.HEIGHT = 1080

        # הטריק: קוראים לקנבס הפנימי 'screen' כדי שכל שאר הקוד שלך יעבוד בלי שינוי
        self.screen = pygame.Surface((self.WIDTH, self.HEIGHT))

        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = None

        # המשתנה שישמור את המצב לכל אורך ריצת המשחק
        self.settings = {
            "music_on": True,
            "sfx_on": True,
            "difficulty": "normal"
        }

    def apply_settings(self):
        # פונקציה מרכזית שמעדכנת את הווליום לפי המשתנה ב-settings
        if self.settings["music_on"]:
            pygame.mixer.music.set_volume(0.5)
        else:
            pygame.mixer.music.set_volume(0.0)

    def run(self, starting_screen):
        self.current_screen = starting_screen

        while self.running:
            # חישוב ה-dt (הזמן שעבר מאז הפריים האחרון בשניות)
            # אם המשחק רץ ב-60 FPS, ה-dt יהיה בערך 0.016
            dt = self.clock.tick(60) / 1000.0

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()

                # --- תרגום מיקום העכבר מהמסך המלא לרזולוציה המקורית ---
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    ratio_x = self.WIDTH / self.WINDOW_WIDTH
                    ratio_y = self.HEIGHT / self.WINDOW_HEIGHT

                    # מעדכנים את המיקום בתוך מילון האירוע כדי שפייתון יאפשר את השינוי
                    event.__dict__['pos'] = (int(event.pos[0] * ratio_x), int(event.pos[1] * ratio_y))

                    # אם זו תזוזה של העכבר, חשוב לעדכן גם את התזוזה היחסית (rel)
                    if event.type == pygame.MOUSEMOTION:
                        event.__dict__['rel'] = (int(event.rel[0] * ratio_x), int(event.rel[1] * ratio_y))

                if self.current_screen:
                    self.current_screen.handle_events(event)

            if self.current_screen:
                # מעבירים את ה-dt לפונקציית ה-update של המסך
                self.current_screen.update(dt)

            # מנקים ומציירים על הקנבס הפנימי (self.screen - בגודל המקורי)
            self.screen.fill((0, 0, 0))
            if self.current_screen:
                self.current_screen.draw()

            # --- שלב המתיחה וההדפסה על המסך (Scaling) ---
            # לוקחים את הקנבס הפנימי ומותחים אותו שיתאים למסך האמיתי
            scaled_surface = pygame.transform.smoothscale(self.screen, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            self.window.blit(scaled_surface, (0, 0))

            pygame.display.flip()

    def change_screen(self, new_screen):
        if self.current_screen:
            self.current_screen.close()
        self.current_screen = new_screen

    def quit(self):
        self.running = False
        if self.current_screen:
            self.current_screen.close()
        pygame.quit()
        sys.exit()