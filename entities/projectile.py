import pygame
import math
import os


class Projectile:
    """
    Represents a projectile (arrow / fireball / bomb / magic ball) in the game.

    The projectile moves toward a target unit and applies damage on hit.
    Visual appearance depends on the shooter type and age.
    """

    def __init__(self, x, y, target, damage, shooter_team, shooter_type, shooter_age="human"):
        """
        Initialize a projectile.

        Args:
            x (int): Starting X position
            y (int): Starting Y position
            target (Unit/BaseTarget): The target to follow and hit
            damage (int): Damage dealt on impact
            shooter_team (str): 'player' or 'enemy'
            shooter_type (str): melee / ranged / flying
            shooter_age (str): unit evolution stage (human, ogre, elf, dragon)
        """
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.shooter_team = shooter_team
        self.speed = 8.0
        self.active = True

        # Default visual fallback values
        image_path = ""
        width, height = 45, 15
        self.color = (0, 0, 0)

        # ===============================
        # Projectile type selection logic
        # ===============================

        # Dragon or Elf ranged/flying -> Fireball
        if (shooter_age == "dragon" and shooter_type in ["ranged", "flying"]) or (
                shooter_age == "elf" and shooter_type == "flying"):
            image_path = "assets/images/projectiles/fireball.png"
            width, height = 35, 35
            self.color = (255, 100, 0)

        # Ogre flying -> Magic ball
        elif shooter_age == "ogre" and shooter_type == "flying":
            image_path = "assets/images/projectiles/magicball.png"
            width, height = 35, 35
            self.color = (138, 43, 226)

        # Default flying units -> Bomb
        elif shooter_type == "flying":
            image_path = "assets/images/projectiles/bomb.png"
            width, height = 35, 35
            self.color = (0, 0, 0)

        # Default ranged attack -> Arrow
        else:
            image_path = "assets/images/projectiles/arrow.png"
            width, height = 45, 15
            self.color = (0, 255, 0) if shooter_team == "player" else (255, 0, 0)

        self.rect = pygame.Rect(x, y, width, height)
        self.image = None

        # Load image if available
        if os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            img = pygame.transform.scale(img, (self.rect.width, self.rect.height))

            # Flip enemy projectiles for correct direction
            if self.shooter_team == "enemy":
                img = pygame.transform.flip(img, True, False)

            self.image = img

    def update(self, dt):
        """
        Updates projectile movement toward its target.

        Args:
            dt (float): Delta time for frame-independent movement (currently unused but kept for consistency)
        """
        if self.target.hp <= 0:
            self.active = False
            return

        # Calculate direction vector toward target
        dx = self.target.rect.centerx - self.x
        dy = self.target.rect.centery - self.y
        dist = math.hypot(dx, dy)

        # If close enough -> apply damage
        if dist < self.speed:
            self.target.hp -= self.damage
            self.active = False
        else:
            # Normalize movement direction
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

    def draw(self, surface):
        """
        Draw the projectile on screen.

        Args:
            surface (pygame.Surface): The surface to draw on
        """
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            # Fallback rectangle if image is missing
            pygame.draw.rect(surface, self.color, self.rect)