import pygame
from button import Button

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.buttons = {}
        self.button_visibility = {}  
        self.font = pygame.font.SysFont(None, 24)

    def add_button(self, id_, rect, text, callback):
        btn = Button(pygame.Rect(rect), text, callback, self.font)
        self.buttons[id_] = btn
        self.button_visibility[id_] = True  

    def set_button_visible(self, id_, visible):
        """Show or hide a button."""
        if id_ in self.button_visibility:
            self.button_visibility[id_] = visible

    def set_buttons_visible_for_state(self, game_state):
        """Show/hide buttons based on game state."""
        if game_state == "MENU":
            self.set_button_visible("start", True)
            self.set_button_visible("save", True)
            self.set_button_visible("load", True)
            self.set_button_visible("credits", True)
            self.set_button_visible("quit", True)
            self.set_button_visible("pause", False)
            self.set_button_visible("back", False)
        elif game_state == "RUNNING":
            self.set_button_visible("start", False)
            self.set_button_visible("save", False)
            self.set_button_visible("load", False)
            self.set_button_visible("credits", False)
            self.set_button_visible("quit", False)
            self.set_button_visible("pause", True)
            self.set_button_visible("back", False)
        elif game_state == "CREDITS":
            self.set_button_visible("start", False)
            self.set_button_visible("save", False)
            self.set_button_visible("load", False)
            self.set_button_visible("credits", False)
            self.set_button_visible("quit", False)
            self.set_button_visible("back", True)
            self.set_button_visible("pause", False)

    def handle_event(self, event):
        for id_, b in self.buttons.items():
            if self.button_visibility.get(id_, False):
                b.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen, player_state=None):
        for id_, b in self.buttons.items():
            if self.button_visibility.get(id_, False):
                b.draw(screen)