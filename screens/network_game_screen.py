import pygame
import threading
import base64
from screens.base_game_screen import BaseGameScreen
from entities.unit import Unit

# Cryptography libraries for secure communication (ECDH + symmetric encryption)
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet


class NetworkGameScreen(BaseGameScreen):
    """
    Online PvP game screen with end-to-end encryption.

    This class is responsible for:
    - Running real-time PvP gameplay
    - Handling network communication with the server
    - Establishing secure encrypted channel (ECDH key exchange)
    - Synchronizing game actions between two players

    Security model:
    - ECDH is used to generate a shared secret key
    - HKDF derives a secure symmetric key from the shared secret
    - Fernet (AES-based) encrypts all gameplay messages
    """

    def __init__(self, game_engine, client_socket, player_num):
        super().__init__(game_engine)

        # -----------------------------
        # Network state
        # -----------------------------
        self.client_socket = client_socket
        self.player_num = player_num
        self.opponent_disconnected = False
        self.network_messages = []

        # Gameplay values
        self.move_speed = 80
        self.enemy_base_rect = pygame.Rect(self.game.WIDTH - 400, self.game.HEIGHT - 650, 700, 600)
        self.enemy_max_hp = 1000
        self.enemy_base_hp = self.enemy_max_hp
        self.enemy_age_index = 0

        # -----------------------------
        # Encryption state
        # -----------------------------
        self.is_encrypted = False
        self.cipher = None

        # =========================================================
        # STEP 1: ECDH KEY GENERATION (local keypair)
        # =========================================================
        # Each client generates a private + public key pair.
        # Private key NEVER leaves the client.
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

        # Convert public key to bytes for network transmission
        self.public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # =========================================================
        # STEP 2: SEND PUBLIC KEY TO SERVER
        # =========================================================
        # Server acts as relay only (does NOT decrypt data)
        try:
            self.client_socket.sendall(b"KEY_EXCHANGE|" + self.public_bytes + b"||")
        except:
            self.opponent_disconnected = True

        # Start listening thread (non-blocking network I/O)
        threading.Thread(target=self.listen_to_server, daemon=True).start()

    # =============================================================
    # ENCRYPTION SETUP (ECDH + HKDF + Fernet)
    # =============================================================
    def setup_encryption(self, peer_public_bytes):
        """
        Establish shared encryption key using Diffie-Hellman (ECDH).

        Flow:
        1. Load opponent public key
        2. Compute shared secret (ECDH)
        3. Derive symmetric AES key using HKDF
        4. Convert key into Fernet-compatible format
        """

        peer_public_key = serialization.load_pem_public_key(peer_public_bytes)

        # ECDH shared secret computation
        shared_key = self.private_key.exchange(ec.ECDH(), peer_public_key)

        # Key derivation (turn raw secret into secure AES key)
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)

        # Fernet requires base64-encoded 32-byte key
        fernet_key = base64.urlsafe_b64encode(derived_key)

        self.cipher = Fernet(fernet_key)
        self.is_encrypted = True

        print("[SECURITY] End-to-End Encryption Established!")

    # =============================================================
    # NETWORK LISTENER THREAD
    # =============================================================
    def listen_to_server(self):
        """
        Background thread that:
        - Receives raw TCP packets
        - Reassembles messages using delimiter (||)
        - Handles key exchange messages
        - Decrypts gameplay messages
        """

        try:
            buffer = b""

            while True:
                data = self.client_socket.recv(4096)
                if not data:
                    break

                buffer += data

                # Split messages by delimiter
                while b"||" in buffer:
                    msg, buffer = buffer.split(b"||", 1)
                    if not msg:
                        continue

                    # -----------------------------------------
                    # KEY EXCHANGE MESSAGE
                    # -----------------------------------------
                    if msg.startswith(b"KEY_EXCHANGE|"):
                        peer_public_bytes = msg.split(b"|", 1)[1]
                        self.setup_encryption(peer_public_bytes)

                    # -----------------------------------------
                    # ENCRYPTED GAME MESSAGE
                    # -----------------------------------------
                    elif self.is_encrypted:
                        try:
                            decrypted_msg = self.cipher.decrypt(msg).decode('utf-8')
                            self.network_messages.append(decrypted_msg)
                        except Exception as e:
                            print(f"Decryption error: {e}")

        except Exception as e:
            print(f"Network error: {e}")

        finally:
            self.opponent_disconnected = True

    # =============================================================
    # SEND ENCRYPTED DATA TO SERVER
    # =============================================================
    def send_data(self, message):
        """
        Encrypts and sends game actions to opponent via server relay.

        Messages are NEVER sent in plaintext after handshake.
        """

        if not self.is_encrypted:
            return

        try:
            encrypted_message = self.cipher.encrypt(message.encode('utf-8'))
            self.client_socket.sendall(encrypted_message + b"||")
        except:
            self.opponent_disconnected = True

    # =============================================================
    # GAME MESSAGE HANDLER
    # =============================================================
    def process_network_message(self, message):
        """
        Parses decrypted commands from opponent.

        Protocol:
        - SPAWN|type
        - EVOLVE
        - SPECIAL
        """

        parts = message.split("|")
        command = parts[0]

        if command == "SPAWN":
            unit_type = parts[1]
            current_enemy_age = self.ages[self.enemy_age_index]

            self.units.append(Unit(
                self.enemy_base_rect.x,
                self.enemy_base_rect.bottom - 150,
                "enemy",
                self.move_speed,
                (255, 0, 0),
                unit_type,
                current_enemy_age
            ))

        elif command == "EVOLVE":
            if self.enemy_age_index < 3:
                self.enemy_age_index += 1

        elif command == "SPECIAL":
            self.trigger_special_power("enemy")

    # =============================================================
    # INPUT HANDLING (PLAYER ACTIONS)
    # =============================================================
    def handle_events(self, event):
        """
        Converts user input into network commands.
        Every action is mirrored to opponent via encrypted packets.
        """

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.go_back()

        # Evolution action
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.player_age_index < 3 and self.player_xp >= self.max_xps[self.player_age_index]:
                if self.evolve_rect.collidepoint(event.pos):
                    self.player_xp -= self.max_xps[self.player_age_index]
                    self.player_age_index += 1
                    self.send_data("EVOLVE")

        current_player_age = self.ages[self.player_age_index]

        # Unit purchases (SPAWN commands)
        if self.buy_melee_btn.is_clicked(event) and self.player_gold >= 100:
            self.player_gold -= 100
            self.units.append(Unit(...))
            self.send_data("SPAWN|melee")

        if self.buy_ranged_btn.is_clicked(event) and self.player_gold >= 125:
            self.player_gold -= 125
            self.units.append(Unit(...))
            self.send_data("SPAWN|ranged")

        if self.buy_flying_btn.is_clicked(event) and self.player_gold >= 150:
            self.player_gold -= 150
            self.units.append(Unit(...))
            self.send_data("SPAWN|flying")

        # Special ability
        current_time = pygame.time.get_ticks()
        if self.special_btn.is_clicked(event) and (
            current_time - self.last_special_time >= self.special_cooldown
        ):
            self.trigger_special_power("player")
            self.last_special_time = current_time
            self.send_data("SPECIAL")

    # =============================================================
    # GAME LOOP UPDATE
    # =============================================================
    def update(self, dt):
        """
        Applies incoming network actions and updates game state.
        """

        if self.opponent_disconnected:
            return

        while self.network_messages:
            msg = self.network_messages.pop(0)
            self.process_network_message(msg)

        super().update(dt)

    # =============================================================
    # DRAW ENEMY BASE UI
    # =============================================================
    def draw(self):
        super().draw()

        enemy_age = self.ages[self.enemy_age_index]
        enemy_base_img = self.base_images.get(enemy_age)

        if enemy_base_img:
            flipped_base = pygame.transform.flip(enemy_base_img, True, False)
            self.game.screen.blit(flipped_base, self.enemy_base_rect)

        # Enemy HP bar rendering
        if self.enemy_base_rect:
            hp_bar_width = 200
            hp_bar_height = 20

            hp_bar_x = self.enemy_base_rect.x + 150
            hp_bar_y = self.enemy_base_rect.y - 30

            ratio = max(0, self.enemy_base_hp / self.enemy_max_hp)

            pygame.draw.rect(self.game.screen, (255, 0, 0),
                             (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(self.game.screen, (0, 255, 0),
                             (hp_bar_x, hp_bar_y, hp_bar_width * ratio, hp_bar_height))
            pygame.draw.rect(self.game.screen, (0, 0, 0),
                             (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)

    # =============================================================
    # EXIT NETWORK GAME SAFELY
    # =============================================================
    def go_back(self):
        """
        Closes network connection and returns to menu.
        Prevents socket leaks and zombie threads.
        """

        try:
            self.client_socket.close()
        except:
            pass

        from screens.mode_selection_screen import ModeSelectionScreen
        self.game.change_screen(ModeSelectionScreen(self.game))