import pygame

pygame.init()


class Button:
    def __init__(self, button_color, button_width, button_height,
                 center_x, center_y, caption="Default text",
                 font=pygame.font.SysFont('consolas', 24, True),
                 text_color=pygame.Color("white")):
        self.button_color = button_color
        self.button_width = button_width
        self.button_height = button_height
        self.center_x = center_x
        self.center_y = center_y
        self.caption = caption
        self.font = font
        self.text_color = text_color

    def draw(self, surface):
        """
        Draw the button on a surface:
            - Fill a rectangle with a certain width, height and color
            - Fill the rectangle at centre coordinates onto the button surface
            - Draw text over the rectangle at its centre on the button surface
            - Draw the button surface onto the target surface
        """
        rect = pygame.Rect((0, 0, self.button_width, self.button_height))
        rect.center = self.center_x, self.center_y
        button_surface = pygame.Surface(rect.size)
        button_surface.fill(self.button_color)

        text_surface = self.font.render(self.caption, True, self.text_color,
                                        self.button_color)
        text_rect = text_surface.get_rect()
        text_rect.center = self.button_width // 2, self.button_height // 2
        button_surface.blit(text_surface, text_rect)

        surface.blit(button_surface, rect)

    def button_clicked(self, event):
        """Return True if the button is clicked"""
        rect = pygame.Rect((0, 0, self.button_width, self.button_height))
        rect.center = self.center_x, self.center_y
        # If the left mouse button is pressed.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            # If the mouse cursor is inside the button area.
            if rect.collidepoint(mouse_pos):
                return True
