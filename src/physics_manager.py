import pygame
class PhysicsManager:
    def __init__(self):
        self.screen_rect = pygame.Rect(0,0,1280,720)

    def update(self, dt, ball_entities):
        for b in ball_entities:
            b.update(dt, self.screen_rect)