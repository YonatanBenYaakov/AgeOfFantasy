import pygame
import time
import os
import socket
import threading
from engine.screen import Screen


class PvPScreen(Screen):
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.start_time = time.time()

        # טעינת תמונת הרקע
        bg_path = "assets/images/screens/waiting_screen.png"
        if os.path.exists(bg_path):
            original_bg = pygame.image.load(bg_path).convert()
            self.bg_img = pygame.transform.scale(original_bg, (self.game.WIDTH, self.game.HEIGHT))
        else:
            self.bg_img = None

        self.font_large = pygame.font.SysFont("Arial", 50, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 30)

        # משתני הרשת
        self.client_socket = None
        self.match_found = False
        self.player_num = 0
        self.connection_error = False

        # הפעלת תהליכון (Thread) שיתחבר לשרת ברקע בלי לתקוע את המסך
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def connect_to_server(self):
        """פונקציה שרצה ברקע, מתחברת לשרת וממתינה לשידוך"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('10.0.0.11', 5555))

            # ברגע שהתחברנו, אנחנו פשוט מחכים שהשרת ידבר איתנו
            while True:
                # מקבלים מידע ומפענחים אותו לטקסט רגיל
                data = self.client_socket.recv(1024).decode('utf-8')

                # אם השרת נסגר או נפל
                if not data:
                    break

                # אם השרת מודיע שמצאנו משחק!
                if data.startswith("MATCH_FOUND"):
                    # מפצלים את ההודעה (למשל "MATCH_FOUND|1") כדי לדעת איזה שחקן אנחנו
                    _, p_num = data.split("|")
                    self.player_num = int(p_num)
                    self.match_found = True
                    break

        except Exception as e:
            print(f"[CLIENT ERROR] Could not connect to server: {e}")
            self.connection_error = True

    def update(self,dt):
        # הלולאה הזו רצה כל הזמן. אם ה-Thread ברקע מצא משחק, נעבור למסך הרשת!
        if self.match_found:
            print(f"Match started! You are Player {self.player_num}")

            from screens.network_game_screen import NetworkGameScreen
            self.game.change_screen(NetworkGameScreen(self.game, self.client_socket, self.player_num))


    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # חשוב לסגור את החיבור לשרת אם אנחנו מתחרטים ויוצאים!
            if self.client_socket:
                try:
                    # שולחים לשרת הודעת ביטול מפורשת כדי שימחק אותנו מיד!
                    self.client_socket.sendall(b"CANCEL")
                    self.client_socket.close()
                except:
                    pass
                self.client_socket = None # חשוב כדי שה-Thread ימות בשקט

            from screens.mode_selection_screen import ModeSelectionScreen
            self.game.change_screen(ModeSelectionScreen(self.game))

    def draw(self):
        if self.bg_img:
            self.game.screen.blit(self.bg_img, (0, 0))
        else:
            self.game.screen.fill((15, 15, 20))

        dots = "." * (int((time.time() - self.start_time) * 2) % 4)

        # שינוי צבע וטקסט לפי מצב החיבור
        if self.connection_error:
            status_msg = "Error: Cannot connect to server"
            color = (255, 50, 50)  # אדום
            dots = ""
        elif self.match_found:
            status_msg = f"Match Found! You are Player {self.player_num}"
            color = (50, 255, 50)  # ירוק
            dots = ""
        else:
            status_msg = "Searching for opponent"
            color = (255, 255, 255)  # לבן

        search_text = self.font_small.render(f"{status_msg}{dots}", True, color)
        cancel_text = self.font_small.render("Press ESC to cancel", True, (180, 180, 180))



        search_rect = search_text.get_rect(bottomleft=(30, self.game.HEIGHT - 30))
        self.game.screen.blit(search_text, search_rect)

        cancel_rect = cancel_text.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT - 50))
        self.game.screen.blit(cancel_text, cancel_rect)