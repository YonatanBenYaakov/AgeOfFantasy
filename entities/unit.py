import pygame
import os


class Unit:
    # הוספנו את age לשורת ההגדרות
    def __init__(self, x, y, team, speed, color, unit_type="melee", age="human"):
        self.team = team
        self.speed = speed
        self.color = color
        self.unit_type = unit_type
        self.age = age  # שומר את סוג העידן

        self.max_hp = 100
        self.hp = self.max_hp
        self.damage = 15
        self.attack_speed = 1000
        self.last_attack_time = 0
        self.is_moving = True
        self.current_state_name = "walk"

        if self.unit_type == "flying":
            self.is_flying, self.can_attack_flying, self.attack_range = True, True, 60
            y -= 80
        elif self.unit_type == "ranged":
            self.is_flying, self.can_attack_flying, self.attack_range = False, True, 150
        else:
            self.is_flying, self.can_attack_flying, self.attack_range = False, False, 15

        self.rect = pygame.Rect(x, y, 100, 120)

        self.animation_frames = {"walk": [], "attack": []}
        self.current_frame = 0
        self.animation_speed = 0.15
        self.last_update = pygame.time.get_ticks()
        self.image = None

        self.load_images()

        if self.animation_frames["walk"]:
            self.image = self.animation_frames["walk"][0]

        # --- הוספת טעינת סאונד ההתקפה מתוך אותה התיקייה ---
        sound_path = f"assets/images/units/{self.age}/{self.unit_type}/attack.wav"
        if os.path.exists(sound_path):
            self.attack_sound = pygame.mixer.Sound(sound_path)
        else:
            self.attack_sound = None

    def play_attack_sound(self, sfx_on):
        """מפעיל את הסאונד רק אם הוא קיים ורק אם השחקן לא השתיק אפקטים"""
        if self.attack_sound and sfx_on:
            self.attack_sound.play()

    def load_images(self):
        base_path = f"assets/images/units/{self.age}/{self.unit_type}"

        for state in ["walk", "attack"]:
            path = f"{base_path}/{state}"
            if os.path.exists(path):
                for file in sorted(os.listdir(path)):
                    if file.endswith(".png"):
                        img = pygame.image.load(f"{path}/{file}").convert_alpha()
                        img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
                        if self.team == "enemy":
                            img = pygame.transform.flip(img, True, False)
                        self.animation_frames[state].append(img)

    def update_animation(self):
        now = pygame.time.get_ticks()
        current_state = "walk" if self.is_moving else "attack"

        if self.current_state_name != current_state:
            self.current_state_name = current_state
            self.current_frame = 0
            self.last_update = now
            if self.animation_frames[current_state]:
                self.image = self.animation_frames[current_state][0]

        frames = self.animation_frames[current_state]
        if frames:
            if now - self.last_update > self.animation_speed * 1000:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.image = frames[self.current_frame]
        else:
            self.image = None

    def can_attack(self, target):
        distance = abs(self.rect.centerx - target.rect.centerx)
        if target.is_flying and not self.can_attack_flying: return False
        return distance <= (self.attack_range + self.rect.width)

    def update(self, dt):  # להוסיף dt כאן
        if self.is_moving:
            # הכפלת המהירות ב-dt גורמת לתנועה להיות לפי זמן ולא לפי פריימים
            if self.team == "player":
                self.rect.x += self.speed * dt
            elif self.team == "enemy":
                self.rect.x -= self.speed * dt

        self.update_animation()

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 10, self.rect.width, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, self.rect.width * hp_ratio, 5))