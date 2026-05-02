import pygame


class Button:
    def __init__(self, x, y, image_path, scale=1.0):
        image = pygame.image.load(image_path).convert_alpha()
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))

        # אנחנו ממקמים את הכפתור לפי המרכז שלו
        self.rect = self.image.get_rect(center=(x, y))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # קליק שמאלי
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)