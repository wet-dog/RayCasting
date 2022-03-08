import pygame
import pickle
from tkinter import filedialog
from gamestates.gamestate import GameState
from gamestates.button import Button
from gamestates.grid import Grid

class MapEditor(GameState):
    def __init__(self):
        super(MapEditor, self).__init__()
        self.next_state = "MENU"

        self.draw_mode = "draw"

        self.bgColor = pygame.Color("black")
        self.title = self.title_font.render("Map Editor", True,
                                            pygame.Color("white"), self.bgColor)
        self.title_rect = self.title.get_rect(center=(self.screen_center_x, 100))

        instructions_str = [
            "Press:",
            " - D to draw, E to erase, P to set spawn,",
            " - Z to undo, R to reset, S to save state,",
            " - CTRL + S to save file, ESC for main menu."
            ]

        self.instructions = []
        for instruct in instructions_str:
            self.instructions.append(
                self.body_font.render(instruct, True, pygame.Color("white"),
                                      self.bgColor)
                )

        self.instructions_rects = []
        for i, instruction in enumerate(self.instructions):
            self.instructions_rects.append(
                instruction.get_rect(topleft=(self.screen_center_x - 215, 600 + i*20))
                )

        self.buttons = {
            "draw": Button(pygame.Color("midnightblue"), 300, 100,
                           self.screen_center_x - 400, 160, "DRAW"),
            "erase": Button(pygame.Color("white"), 300, 100,
                            self.screen_center_x - 400, 260, "ERASE",
                            text_color=pygame.Color("black")),
            "set spawn": Button(pygame.Color("chartreuse3"), 300, 100,
                                self.screen_center_x - 400, 360, "SET SPAWN"),
            "undo": Button(pygame.Color("purple4"), 300, 100,
                           self.screen_center_x - 400, 460, "UNDO"),
            "reset": Button(pygame.Color("deeppink"), 300, 100,
                            self.screen_center_x - 400, 560, "RESET"),
            "save state": Button(pygame.Color("orange"), 300, 100,
                                 self.screen_center_x + 400, 275, "SAVE STATE"),
            "save file": Button(pygame.Color("mediumvioletred"), 300, 100,
                                self.screen_center_x + 400, 375, "SAVE FILE"),
            "menu": Button(pygame.Color("red"), 300, 100,
                           self.screen_center_x + 400, 475, "MENU")
            }

    def set_spawn(self):
        """
        Find what position in the 2D array has been set to -1 (spawn)
        and set the spawn point variable to its position in the array.
        """
        for j, row in enumerate(self.grid.map):
            for i, cell in enumerate(row):
                if cell == -1:
                    self.spawn_point = (j+1, i+1)
                    self.persist["spawn_point"] = self.spawn_point

    def save_state(self):
        """Save the state of the grid map to the persistent map array."""
        # A list comprehension is used so changing self.grid.map doesn't directly
        # change self.persist["map"] without save_state() being called.
        self.persist["map"] = [list(x) for x in self.grid.map]
        self.set_spawn()

    def save_file(self):
        """Save the map array to a file."""
        self.save_state()
        file_path = filedialog.asksaveasfilename()  # run a save file dialog
        if file_path:   # check if a file is actually being saved to
            with open(file_path, "wb") as fp:
                pickle.dump(self.persist["map"], fp)

    def startup(self, persistent):
        super().startup(persistent)
        # Make the mouse cursor visible so the user can click buttons.
        pygame.mouse.set_visible(True)
        # Create a grid with cell size 15 and cell gap size 2.
        self.grid = Grid(self.persist["map"], 15, 2)
        self.set_spawn()
        self.save_state()

    def get_event(self, event):
        super().get_event(event)

        if event.type == pygame.MOUSEBUTTONUP:
            # If any cells have been modified since mouse button was held down
            # then add those cells to the modified cells stack.
            if self.grid.recent_cell_indexes:
                self.grid.clicked_cells.append(self.grid.recent_cell_indexes)
            # Reset list of cells modified since mouse button has been pressed.
            self.grid.recent_cell_indexes = []

        # Z key is checked here instead of in update() so only one undo happens
        # per key press.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.grid.undo()

        if self.buttons["draw"].button_clicked(event):
            self.draw_mode = "draw"
        elif self.buttons["erase"].button_clicked(event):
            self.draw_mode = "erase"
        elif self.buttons["set spawn"].button_clicked(event):
            self.draw_mode = "set spawn"
        elif self.buttons["undo"].button_clicked(event):
            self.grid.undo()
        elif self.buttons["reset"].button_clicked(event):
            self.grid.reset()
        elif self.buttons["save state"].button_clicked(event):
            self.save_state()
        elif self.buttons["save file"].button_clicked(event):
            self.save_file()
        elif self.buttons["menu"].button_clicked(event):
            self.done = True

    def update(self, dt):
        # Print FPS
        # print(dt)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.done = True

        if keys[pygame.K_d]:
            self.draw_mode = "draw"
        if keys[pygame.K_e]:
            self.draw_mode = "erase"
        if keys[pygame.K_p]:
            self.draw_mode = "set spawn"
        if keys[pygame.K_r]:
            self.grid.reset()

        if keys[pygame.K_s] and keys[pygame.K_LCTRL]:
            self.save_file()
        elif keys[pygame.K_s]:
            self.save_state()

    def draw(self, surface):
        surface.fill(self.bgColor)
        surface.blit(self.title, self.title_rect)

        # Draw instructions text to the surface (screen).
        for instruct, rect in zip(self.instructions, self.instructions_rects):
            surface.blit(instruct, rect)

        self.grid.cell_clicked(surface, self.draw_mode)
        self.grid.draw(surface)

        # Draw every button to the surface (screen).
        for button in self.buttons.values():
            button.draw(surface)
