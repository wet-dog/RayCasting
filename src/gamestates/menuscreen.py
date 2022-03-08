import pygame
from gamestates.gamestate import GameState
from gamestates.button import Button

class MenuScreen(GameState):
    def __init__(self):
        super(MenuScreen, self).__init__()

        self.bgColor = pygame.Color("black")
        self.title = self.title_font.render("Ray Casting Engine Menu", True,
                                            pygame.Color("white"), self.bgColor)
        self.title_rect = self.title.get_rect(center=(self.screen_center_x, 100))

        self.multi_text = self.sub_font.render("Multiplayer", True,
                                               pygame.Color("white"), self.bgColor)
        self.multi_rect = self.multi_text.get_rect(center=(
                                                self.screen_center_x + 250, 190))

        self.buttons = {
            "play": Button(pygame.Color("green"), 300, 100,
                           self.screen_center_x, 250, "PLAY"),
            "load map": Button(pygame.Color("gold"), 300, 100,
                               self.screen_center_x, 350, "LOAD MAP"),
            "map editor": Button(pygame.Color("orange"), 300, 100,
                                 self.screen_center_x, 450, "MAP EDITOR"),
            "exit": Button(pygame.Color("red"), 300, 100,
                           self.screen_center_x, 550, "EXIT"),
            "multi": Button(pygame.Color("red"), 75, 50,
                            self.multi_rect.centerx, 250, "NO")
            }

        self.multi_button_colors = [pygame.Color("red"), pygame.Color("green")]
        self.multi_button_captions = ["NO", "YES"]

    def startup(self, persistent):
        super().startup(persistent)
        # Make the mouse cursor visible so the user can click buttons.
        pygame.mouse.set_visible(True)

    def get_event(self, event):
        super().get_event(event)

        if self.buttons["play"].button_clicked(event):
            self.next_state = "GAMEPLAY"
            self.done = True
        elif self.buttons["multi"].button_clicked(event):
            # Make multi_flag the opposite of what it already is:
            # i.e. 0 --> 1 or 1 --> 0
            self.persist["multi_flag"] = not self.persist["multi_flag"]
            # Change the color and caption of the toggle button to what
            # corresponds with multi_flag's state.
            color = self.multi_button_colors[self.persist["multi_flag"]]
            caption = self.multi_button_captions[self.persist["multi_flag"]]
            self.buttons["multi"].button_color = color
            self.buttons["multi"].caption = caption
        elif self.buttons["load map"].button_clicked(event):
            self.next_state = "LOAD MAP"
            self.done = True
        elif self.buttons["map editor"].button_clicked(event):
            self.next_state = "MAP EDITOR"
            self.done = True
        elif self.buttons["exit"].button_clicked(event):
            self.quit = True

    def draw(self, surface):
        surface.fill(self.bgColor)
        surface.blit(self.title, self.title_rect)
        surface.blit(self.multi_text, self.multi_rect)

        # Draw every button to the surface (screen).
        for button in self.buttons.values():
            button.draw(surface)
