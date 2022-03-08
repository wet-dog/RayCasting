import sys
import pygame
import tkinter as tk
from gamestates.gamestate import GameState
from gamestates.menuscreen import MenuScreen 
from gamestates.loadmap import LoadMap
from gamestates.mapeditor import MapEditor
from gamestates.gameplay import Gameplay

# Initialize and hide tkinter root window
root = tk.Tk()
root.withdraw()


class Game:
    def __init__(self, states, start_state):
        self.done = False
        self.screen = pygame.display.set_mode((0, 0))
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.states = states
        self.state_name = start_state
        self.state = self.states[self.state_name]

    def event_loop(self):
        """Gets pygame events and passes them to a gamestate."""
        for event in pygame.event.get():
            self.state.get_event(event)

    def change_state(self):
        """Change from one game state to another."""
        # Pass the persistent variables of the previous state to the next state.
        persistent = self.state.persist
        self.state = self.states[self.state.next_state]
        self.state.startup(persistent)

    def update(self, dt):
        """
        Update the gamestate, check if the whole program has been quit or if
        that particular gamestate is done.
        """
        # If a state sets state.quit to True then the whole program will exit.
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.change_state()
        self.state.update(dt)

    def draw(self):
        """Draw a gamestate to the screen."""
        self.state.draw(self.screen)

    def run(self):
        """
        Infinite while loop that runs all the functions of the game until the
        user exits.
        """
        while not self.done:
            # dt - change in time between each frame is found.
            dt = self.clock.tick(self.fps)
            self.event_loop()
            self.update(dt)
            self.draw()
            pygame.display.update()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    states = {"MENU": MenuScreen(), "GAMEPLAY": Gameplay(),
              "LOAD MAP": LoadMap(), "MAP EDITOR": MapEditor()}
    game = Game(states, "MENU")
    game.run()
    pygame.quit()
    sys.exit()
