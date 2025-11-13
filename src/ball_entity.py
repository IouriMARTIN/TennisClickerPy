import pygame, random, math
class BallEntity:
    def __init__(self, x, y, vx, vy, radius=12, value=1.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.value = value

    def update(self, dt, screen_rect):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x - self.radius < screen_rect.left:
            self.x = screen_rect.left + self.radius
            self.vx = -self.vx * 1.0
            self.vx += (random.random()-0.5)*30
        if self.x + self.radius > screen_rect.right:
            self.x = screen_rect.right - self.radius
            self.vx = -self.vx * 1.0
            self.vx += (random.random()-0.5)*30
        if self.y - self.radius < screen_rect.top:
            self.y = screen_rect.top + self.radius
            self.vy = -self.vy * 1.0
            self.vy += (random.random()-0.5)*30
        if self.y + self.radius > screen_rect.bottom:
            self.y = screen_rect.bottom - self.radius
            self.vy = -self.vy * 1.0
            self.vy += (random.random()-0.5)*30

    def draw(self, screen):
        pygame.draw.circle(screen, (255,225,25), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), self.radius, 2)
