import pygame
import pickle
from tkinter import filedialog
from gamestates.gamestate import GameState
from gamestates.button import Button
from maps.example_maps import default_map

class LoadMap(GameState):
    def __init__(self):
        super(LoadMap, self).__init__()
        self.next_state = "MAP EDITOR"

        self.bgColor = pygame.Color("black")
        self.title = self.title_font.render("Load", True, pygame.Color("white"),
                                            self.bgColor)
        self.title_rect = self.title.get_rect(center=(self.screen_center_x, 100))

        self.buttons = {
            "existing map": Button(pygame.Color("orange"), 300, 100,
                                   self.screen_center_x, 300, "EXISTING MAP"),
            "default map": Button(pygame.Color("blue"), 300, 100,
                                  self.screen_center_x, 400, "DEFAULT MAP"),
            "menu": Button(pygame.Color("red"), 300, 100,
                           self.screen_center_x, 500, "MENU")
            }

    def open_map(self):
        """Open a map from a file into the map variable."""
        file_path = filedialog.askopenfilename()    # Run an open file dialog.
        if file_path:   # Check if a file has actually been loaded.
            with open(file_path, "rb") as fp:
                map = pickle.load(fp)
                return map

    def has_border(self, map):
        """If the map has a border of 1s return True if not return False."""
        # True if the first row is all 1s, otherwise False.
        first_row = all(map[0])
        # True if the last row is all 1s, otherwise False.
        last_row = all(map[-1])
        # True if the first number of every row is a 1, otherwise False.
        first_ele = all([row[0] for row in map])
        # True if the last number of every row is a 1, otherwise False.
        last_ele = all([row[-1] for row in map])

        return first_row and last_row and first_ele and last_ele

    def add_border(self, map):
        """Add a border of 1s around the map."""
        # Add a row of 1s to the start of the map array.
        map.insert(0, [1 for i in range(len(map[0]))])
        # Add a row of 1s to the end of the map array.
        map.append([1 for i in range(len(map[0]))])
        # For every row in the map array add a 1 to the start and end of it.
        for row in map:
            row.insert(0, 1)
            row.append(1)

    def startup(self, persistent):
        super().startup(persistent)
        # Make the mouse cursor visible so the user can click buttons.
        pygame.mouse.set_visible(True)

    def get_event(self, event):
        super().get_event(event)

        if self.buttons["existing map"].button_clicked(event):
            map = self.open_map()
            if map:                            # Check if map has been loaded
                if not self.has_border(map):
                    self.add_border(map)

                self.persist["map"] = map

            self.done = True
        elif self.buttons["default map"].button_clicked(event):
            self.persist["map"] = default_map
            self.done = True
        elif self.buttons["menu"].button_clicked(event):
            self.next_state = "MENU"
            self.done = True

    def draw(self, surface):
        surface.fill(self.bgColor)
        surface.blit(self.title, self.title_rect)

        # Draw every button to the surface (screen).
        for button in self.buttons.values():
            button.draw(surface)
