import pygame


class Button:
    """
    Simple UI Button class for handling:
    - Image-based buttons
    - Click detection
    - Rendering to screen
    """

    def __init__(self, x, y, image_path, scale=1.0):
        """
        Initialize a button.

        Args:
            x (int): X position of button center
            y (int): Y position of button center
            image_path (str): Path to button image
            scale (float): Scale factor for resizing the image
        """

        # Load button image with alpha transparency
        image = pygame.image.load(image_path).convert_alpha()

        # Resize image according to scale
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)

        self.image = pygame.transform.scale(image, (width, height))

        # Center-based positioning
        self.rect = self.image.get_rect(center=(x, y))

    def is_clicked(self, event):
        """
        Check if the button was clicked.

        Args:
            event (pygame.Event): Input event

        Returns:
            bool: True if left mouse button clicked on this button
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface):
        """
        Draw the button on a given surface.

        Args:
            surface (pygame.Surface): Surface to render the button on
        """
        surface.blit(self.image, self.rect)