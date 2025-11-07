import pygame
from button import Button

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.buttons = {}
        self.font = pygame.font.SysFont(None, 24)

    def add_button(self, id_, rect, text, callback):
        btn = Button(pygame.Rect(rect), text, callback, self.font)
        self.buttons[id_] = btn

    def handle_event(self, event):
        for b in self.buttons.values():
            b.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, screen, player_state=None):
        for b in self.buttons.values():
            b.draw(screen)
        # optionally draw player info small
        if player_state:
            txt = self.font.render(f"Click power: {player_state.click_power}", True, (255,255,255))
            screen.blit(txt, (50, 260))