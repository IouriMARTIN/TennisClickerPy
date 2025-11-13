import pygame

class Button:
    def __init__(self, rect, text, callback, font):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.font = font
        self.hover = False
        self.pressed = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                try:
                    self.callback()
                except Exception as e:
                    print("Button callback error:", e)
            self.pressed = False

    def draw(self, screen):
        color = (200,200,200)
        if self.pressed:
            color = (160,160,160)
        elif self.hover:
            color = (220,220,220)
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        txt = self.font.render(self.text, True, (0,0,0))
        tw, th = txt.get_size()
        screen.blit(txt, (self.rect.x + (self.rect.w - tw)//2, self.rect.y + (self.rect.h - th)//2))