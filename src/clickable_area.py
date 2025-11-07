import pygame, math
class ClickableArea:
    def __init__(self, center, radius, player):
        self.x, self.y = center
        self.radius = radius
        self.player = player
        self.scale = 1.0
        self.anim_t = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if (mx - self.x)**2 + (my - self.y)**2 <= (self.radius*self.scale)**2:
                self.player.points += self.player.click_power * self.player.global_multiplier
                # simple pop animation
                self.scale = 0.85
                self.anim_t = 0.12

    def update(self, dt):
        if self.anim_t > 0:
            self.anim_t -= dt
            if self.anim_t <= 0:
                self.scale = 1.0

    def draw(self, screen):
        # draw tennis ball as yellow circle with white seams
        r = int(self.radius * self.scale)
        pygame.draw.circle(screen, (255, 225, 25), (int(self.x), int(self.y)), r)
        pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), r, 3)
        # seam arcs (very simple)
        pygame.draw.arc(screen, (255,255,255), (self.x-r, self.y-r, r*2, r*2), 0.5, 2.6, 2)