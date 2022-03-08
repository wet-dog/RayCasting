import pygame

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)


class Grid:
    def __init__(self, map, cell_size, cell_gap_size):
        # List comprehension to make a copy instead of referencing original object.
        self.map = [list(x) for x in map]
        self.cells_x = len(self.map[0])
        self.cells_y = len(self.map)
        self.cell_size = cell_size
        self.cell_gap_size = cell_gap_size
        self.grid_width = (self.cells_x*cell_size + (self.cells_x*cell_gap_size
                                                     - cell_gap_size))
        self.grid_height = (self.cells_y*cell_size + (self.cells_y*cell_gap_size
                                                      - cell_gap_size))
        self.grid_rect = pygame.Rect((0, 0, self.grid_width, self.grid_height))
        self.grid_surface = pygame.Surface(self.grid_rect.size)

        # List to keep track of coordinates of cells modified in last mouse press
        self.recent_cell_indexes = []
        # Stack of lists of coordinates of cells modified in different mouse presses
        self.clicked_cells = []

        self.cells = [[] for y in range(self.cells_y)]

    def align(self, surface):
        """Move the center of each cell to where it has actually been drawn."""
        surface_width = surface.get_width()
        surface_height = surface.get_height()
        for row in self.cells:
            for cell in row:
                cell["rect"].centerx += surface_width // 2 - self.grid_width // 2
                cell["rect"].centery += surface_height // 2 - self.grid_height // 2
        self.grid_rect.center = surface_width // 2, surface_height // 2

    def draw(self, surface):
        """Draw the grid from scratch every frame."""

        # Reset 2D array of cells
        self.cells = [[] for y in range(self.cells_y)]

        colors = {"empty": pygame.Color("white"), "wall": pygame.Color("red"),
                  "spawn": pygame.Color("green")}
        types = {-1: "spawn", 0: "empty", 1: "wall"}

        # Create and add cells to the 2D cells array.
        for y, row in enumerate(self.map):
            for x, ele in enumerate(row):
                rect = pygame.Rect(x*(self.cell_size + self.cell_gap_size),
                                   y*(self.cell_size + self.cell_gap_size),
                                   self.cell_size, self.cell_size)
                cell = {"rect": rect, "type": types[1],
                        "color": colors[types[ele]]}
                self.cells[y].append(cell)

        # Draw the cells of the grid to a surface.
        for row in self.cells:
            for cell in row:
                pygame.draw.rect(self.grid_surface, cell["color"], cell["rect"])

        self.align(surface)
        surface.blit(self.grid_surface, self.grid_rect)

    def undo(self):
        """Undo every changed cell since the mouse button was held down."""
        # Check cells have been modified
        if self.clicked_cells:
            # Get coords of all modified cells
            for coords in self.clicked_cells[-1]:
                i = coords[0]
                j = coords[1]
                # Reverse fill of cell
                self.map[j][i] = int(not self.map[j][i])

            # Remove undone cells from the modified cells stack.
            self.clicked_cells.pop()

    def reset(self):
        """Reset every cell in map to a fill of 0 excluding the border cells."""
        # [1:-1] and enumerate starts at 1 so border cells not affected
        for j, row in enumerate(self.cells[1:-1], 1):
            for i, cell in enumerate(row[1:-1], 1):
                # Only set fill of cell to 0 if cell isn't already 0
                if self.map[j][i]:
                    self.map[j][i] = 0
                    # add reset cells to recently change cells list
                    self.recent_cell_indexes.append((i, j))

    def cell_clicked(self, surface, mode):
        """
        Check if a cell has been clicked and then fill it depending on the
        current drawing mode: drawing walls, erasing or setting the spawn.
        """
        # Check if spawn already set and if it is return
        if mode == "set spawn":
            if any(-1 in row for row in self.map):
                return

        # If left mouse button pressed
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()

            # Change what the cell will be filled with based on the draw mode.
            modes = {"draw": 1, "erase": 0,  "set spawn": -1}
            fill = modes[mode]
            # [1:-1] and enumerate start at 1 so border cells not affected
            for j, row in enumerate(self.cells[1:-1], 1):
                for i, cell in enumerate(row[1:-1], 1):
                    # If mouse pointer is in a cell.
                    if cell["rect"].collidepoint(mouse_pos):
                        # Check if a change is actually being made to the cell.
                        if fill != self.map[j][i]:
                            self.map[j][i] = fill
                            # Add the coordinates of the cell modified to the
                            # recently modified cells list.
                            self.recent_cell_indexes.append((i, j))
