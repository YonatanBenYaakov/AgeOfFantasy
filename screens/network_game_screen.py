import pygame
import threading
import base64
from screens.base_game_screen import BaseGameScreen
from entities.unit import Unit

# ספריות ההצפנה החדשות שלנו
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.fernet import Fernet


class NetworkGameScreen(BaseGameScreen):
    def __init__(self, game_engine, client_socket, player_num):
        super().__init__(game_engine)
        self.client_socket = client_socket
        self.player_num = player_num
        self.opponent_disconnected = False
        self.network_messages = []

        self.move_speed = 80
        self.enemy_base_rect = pygame.Rect(self.game.WIDTH - 400, self.game.HEIGHT - 650, 700, 600)
        self.enemy_max_hp = 1000
        self.enemy_base_hp = self.enemy_max_hp
        self.enemy_age_index = 0

        # --- מנגנון ההצפנה (ECDH) ---
        self.is_encrypted = False
        self.cipher = None

        # 1. ייצור המפתח הפרטי והציבורי שלנו (במהירות האור)
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()
        self.public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # 2. שולחים את המפתח הציבורי ליריב דרך השרת בתור הודעה ראשונה!
        try:
            self.client_socket.sendall(b"KEY_EXCHANGE|" + self.public_bytes + b"||")
        except:
            self.opponent_disconnected = True

        threading.Thread(target=self.listen_to_server, daemon=True).start()

    def setup_encryption(self, peer_public_bytes):
        """פונקציה שמחשבת את המפתח המשותף ברגע שקיבלנו את המפתח של היריב"""
        # טוענים את המפתח הציבורי של היריב
        peer_public_key = serialization.load_pem_public_key(peer_public_bytes)

        # דיפי הלמן בפעולה - יוצרים את הסוד המשותף!
        shared_key = self.private_key.exchange(ec.ECDH(), peer_public_key)

        # הופכים את הסוד למפתח הצפנה תקני (32 בתים) עבור Fernet
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)

        fernet_key = base64.urlsafe_b64encode(derived_key)
        self.cipher = Fernet(fernet_key)
        self.is_encrypted = True
        print("[SECURITY] End-to-End Encryption Established!")

    def listen_to_server(self):
        """ההאזנה לשרת - כעת עובדת עם באפר בטוח בגלל ההצפנה"""
        try:
            buffer = b""
            while True:
                data = self.client_socket.recv(4096)  # באפר מוגדל
                if not data: break

                buffer += data

                # מחלצים הודעות שלמות שמסתיימות במפריד שלנו
                while b"||" in buffer:
                    msg, buffer = buffer.split(b"||", 1)
                    if not msg: continue

                    # בדיקה האם זו הודעת לחיצת יד של דיפי-הלמן
                    if msg.startswith(b"KEY_EXCHANGE|"):
                        peer_public_bytes = msg.split(b"|", 1)[1]
                        self.setup_encryption(peer_public_bytes)

                    # אם זו הודעה רגילה (וההצפנה כבר מוכנה)
                    elif self.is_encrypted:
                        try:
                            # פתיחת ההצפנה
                            decrypted_msg = self.cipher.decrypt(msg).decode('utf-8')
                            self.network_messages.append(decrypted_msg)
                        except Exception as e:
                            print(f"Decryption error: {e}")

        except Exception as e:
            print(f"Network error: {e}")
        finally:
            self.opponent_disconnected = True

    def send_data(self, message):
        """פונקציית השליחה - מצפינה לפני שהיא יורה את המידע לשרת"""
        if not self.is_encrypted:
            return  # לא שולחים כלום (גם לא בטעות) עד שיש אישור אבטחה

        try:
            encrypted_message = self.cipher.encrypt(message.encode('utf-8'))
            self.client_socket.sendall(encrypted_message + b"||")
        except:
            self.opponent_disconnected = True

    def process_network_message(self, message):
        parts = message.split("|")
        command = parts[0]

        if command == "SPAWN":
            unit_type = parts[1]
            current_enemy_age = self.ages[self.enemy_age_index]
            new_unit = Unit(self.enemy_base_rect.x, self.enemy_base_rect.bottom - 150,
                            "enemy", self.move_speed, (255, 0, 0), unit_type, current_enemy_age)
            self.units.append(new_unit)

        elif command == "EVOLVE":
            if self.enemy_age_index < 3:
                self.enemy_age_index += 1

        elif command == "SPECIAL":
            self.trigger_special_power("enemy")

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.go_back()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.player_age_index < 3 and self.player_xp >= self.max_xps[self.player_age_index]:
                if self.evolve_rect.collidepoint(event.pos):
                    self.player_xp -= self.max_xps[self.player_age_index]
                    self.player_age_index += 1
                    self.send_data("EVOLVE")

        current_player_age = self.ages[self.player_age_index]

        if self.buy_melee_btn.is_clicked(event) and self.player_gold >= 100:
            self.player_gold -= 100
            self.units.append(Unit(self.player_base_rect.x + 350, self.player_base_rect.bottom - 150,
                                   "player", self.move_speed, (0, 0, 255), "melee", current_player_age))
            self.send_data("SPAWN|melee")

        if self.buy_ranged_btn.is_clicked(event) and self.player_gold >= 125:
            self.player_gold -= 125
            self.units.append(Unit(self.player_base_rect.x + 350, self.player_base_rect.bottom - 150,
                                   "player", self.move_speed, (0, 255, 0), "ranged", current_player_age))
            self.send_data("SPAWN|ranged")

        if self.buy_flying_btn.is_clicked(event) and self.player_gold >= 150:
            self.player_gold -= 150
            self.units.append(Unit(self.player_base_rect.x + 350, self.player_base_rect.bottom - 150,
                                   "player", self.move_speed, (0, 255, 255), "flying", current_player_age))
            self.send_data("SPAWN|flying")

        current_time = pygame.time.get_ticks()
        if self.special_btn.is_clicked(event) and (current_time - self.last_special_time >= self.special_cooldown):
            self.trigger_special_power("player")
            self.last_special_time = current_time
            self.send_data("SPECIAL")

    def update(self, dt):
        if self.opponent_disconnected:
            return

        while len(self.network_messages) > 0:
            msg = self.network_messages.pop(0)
            self.process_network_message(msg)

        super().update(dt)

    def draw(self):
        super().draw()
        enemy_age = self.ages[self.enemy_age_index]
        enemy_base_img = self.base_images.get(enemy_age)

        if enemy_base_img and self.enemy_base_rect:
            flipped_base = pygame.transform.flip(enemy_base_img, True, False)
            self.game.screen.blit(flipped_base, self.enemy_base_rect)

        if self.enemy_base_rect:
            hp_bar_width = 200
            hp_bar_height = 20
            hp_bar_x = self.enemy_base_rect.x + 150
            hp_bar_y = self.enemy_base_rect.y - 30
            e_hp_ratio = max(0, self.enemy_base_hp / self.enemy_max_hp)

            pygame.draw.rect(self.game.screen, (255, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(self.game.screen, (0, 255, 0),
                             (hp_bar_x, hp_bar_y, hp_bar_width * e_hp_ratio, hp_bar_height))
            pygame.draw.rect(self.game.screen, (0, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)

    def go_back(self):
        try:
            self.client_socket.close()
        except:
            pass
        from screens.mode_selection_screen import ModeSelectionScreen
        self.game.change_screen(ModeSelectionScreen(self.game))