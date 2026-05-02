import pygame
import math
import os


class Projectile:
    def __init__(self, x, y, target, damage, shooter_team, shooter_type, shooter_age="human"):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.shooter_team = shooter_team
        self.speed = 8.0
        self.active = True

        # --- בחירת תמונה וגודל לפי העידן וסוג היורה ---
        image_path = ""
        width, height = 45, 15  # מידות ברירת מחדל לחץ
        self.color = (0, 0, 0)

        # דרקון (רחוק ומעופף) או אלף (מעופף) -> Fireball
        if (shooter_age == "dragon" and shooter_type in ["ranged", "flying"]) or (
                shooter_age == "elf" and shooter_type == "flying"):
            image_path = "assets/images/projectiles/fireball.png"
            width, height = 35, 35
            self.color = (255, 100, 0)  # כתום אש לגיבוי

        # אוגר (מעופף) -> Magicball
        elif shooter_age == "ogre" and shooter_type == "flying":
            image_path = "assets/images/projectiles/magicball.png"
            width, height = 35, 35
            self.color = (138, 43, 226)  # סגול קסם לגיבוי

        # ברירת מחדל לכל שאר המעופפים (כמו human) -> Bomb
        elif shooter_type == "flying":
            image_path = "assets/images/projectiles/bomb.png"
            width, height = 35, 35
            self.color = (0, 0, 0)

        # ברירת מחדל לכל שאר הרחוקים -> Arrow
        else:
            image_path = "assets/images/projectiles/arrow.png"
            width, height = 45, 15
            self.color = (0, 255, 0) if shooter_team == "player" else (255, 0, 0)

        self.rect = pygame.Rect(x, y, width, height)
        self.image = None

        # --- טעינת התמונה אם היא קיימת ---
        if os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            img = pygame.transform.scale(img, (self.rect.width, self.rect.height))

            # הפיכת התמונה אם זה האויב יורה
            if self.shooter_team == "enemy":
                img = pygame.transform.flip(img, True, False)
            self.image = img

    def update(self,dt):
        if self.target.hp <= 0:
            self.active = False
            return

        dx = self.target.rect.centerx - self.x
        dy = self.target.rect.centery - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.target.hp -= self.damage
            self.active = False
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            # גיבוי: מצייר מלבן אם לא קיימת תמונה
            pygame.draw.rect(surface, self.color, self.rect)