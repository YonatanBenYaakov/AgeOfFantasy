import pygame
import time
import os
import socket
import threading
from engine.screen import Screen


class PvPScreen(Screen):
    """
    PvP matchmaking screen.

    This screen is responsible for:
    - Connecting to the matchmaking server
    - Waiting for an opponent
    - Handling cancel/disconnect logic
    - Transitioning to the network game when a match is found

    Networking is handled in a background thread to prevent UI freezing.
    """

    def __init__(self, game_engine):
        super().__init__(game_engine)

        # Track waiting start time (for UI animation)
        self.start_time = time.time()

        # -----------------------------
        # Background image setup
        # -----------------------------
        bg_path = "assets/images/screens/waiting_screen.png"
        if os.path.exists(bg_path):
            original_bg = pygame.image.load(bg_path).convert()
            self.bg_img = pygame.transform.scale(original_bg, (self.game.WIDTH, self.game.HEIGHT))
        else:
            self.bg_img = None

        # Fonts for UI rendering
        self.font_large = pygame.font.SysFont("Arial", 50, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 30)

        # -----------------------------
        # Network state variables
        # -----------------------------
        self.client_socket = None       # TCP socket to server
        self.match_found = False        # Flag when server pairs player
        self.player_num = 0             # Assigned player ID (1 or 2)
        self.connection_error = False    # Connection failure flag

        # Start connection thread (non-blocking networking)
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def connect_to_server(self):
        """
        Background thread that handles:
        - Connecting to matchmaking server
        - Waiting for MATCH_FOUND message
        - Parsing assigned player number
        """

        try:
            # Create TCP connection to matchmaking server
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('10.0.0.11', 5555))

            # Listen for server messages continuously
            while True:
                data = self.client_socket.recv(1024).decode('utf-8')

                # Server disconnected
                if not data:
                    break

                # Match found message format: MATCH_FOUND|1 or MATCH_FOUND|2
                if data.startswith("MATCH_FOUND"):
                    _, p_num = data.split("|")
                    self.player_num = int(p_num)
                    self.match_found = True
                    break

        except Exception as e:
            # Connection failed (server down / network issue)
            print(f"[CLIENT ERROR] Could not connect to server: {e}")
            self.connection_error = True

    def update(self, dt):
        """
        Game loop update.

        If a match has been found by the network thread,
        transition to the actual PvP gameplay screen.
        """

        if self.match_found:
            print(f"Match started! You are Player {self.player_num}")

            from screens.network_game_screen import NetworkGameScreen
            self.game.change_screen(
                NetworkGameScreen(self.game, self.client_socket, self.player_num)
            )

    def handle_events(self, event):
        """
        Handles user input.

        ESC key:
        - Cancels matchmaking
        - Sends CANCEL packet to server
        - Closes socket safely
        - Returns to mode selection screen
        """

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:

            # Notify server we are leaving queue
            if self.client_socket:
                try:
                    self.client_socket.sendall(b"CANCEL")
                    self.client_socket.close()
                except:
                    pass

                # Important: prevent background thread usage after close
                self.client_socket = None

            from screens.mode_selection_screen import ModeSelectionScreen
            self.game.change_screen(ModeSelectionScreen(self.game))

    def draw(self):
        """
        Renders matchmaking UI:
        - Background image
        - Searching animation (dots)
        - Status messages (searching / matched / error)
        - Cancel instruction
        """

        if self.bg_img:
            self.game.screen.blit(self.bg_img, (0, 0))
        else:
            self.game.screen.fill((15, 15, 20))

        # Animated dots for "Searching..."
        dots = "." * (int((time.time() - self.start_time) * 2) % 4)

        # -----------------------------
        # UI state logic
        # -----------------------------
        if self.connection_error:
            status_msg = "Error: Cannot connect to server"
            color = (255, 50, 50)
            dots = ""

        elif self.match_found:
            status_msg = f"Match Found! You are Player {self.player_num}"
            color = (50, 255, 50)
            dots = ""

        else:
            status_msg = "Searching for opponent"
            color = (255, 255, 255)

        # Render text
        search_text = self.font_small.render(f"{status_msg}{dots}", True, color)
        cancel_text = self.font_small.render("Press ESC to cancel", True, (180, 180, 180))

        # Position text
        search_rect = search_text.get_rect(bottomleft=(30, self.game.HEIGHT - 30))
        cancel_rect = cancel_text.get_rect(center=(self.game.WIDTH // 2, self.game.HEIGHT - 50))

        # Draw UI
        self.game.screen.blit(search_text, search_rect)
        self.game.screen.blit(cancel_text, cancel_rect)