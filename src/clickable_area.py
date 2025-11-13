import pygame


class ClickableArea:
    def __init__(self, center, radius, player):
        self.x, self.y = center
        self.radius = radius
        self.player = player
        self.scale = 1.0
        self.target_scale = 1.0
        self.hovered = False
        # cache scaled images to avoid repeated transforms
        self._scaled_cache = {}

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            # hover detection uses base radius so visual scale doesn't affect hit test
            self.hovered = (mx - self.x) ** 2 + (my - self.y) ** 2 <= (self.radius) ** 2
            self.target_scale = 1.12 if self.hovered else 1.0
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if (mx - self.x) ** 2 + (my - self.y) ** 2 <= (self.radius) ** 2:
                # award points on click; do not shrink the ball
                self.player.points += self.player.click_power * self.player.global_multiplier
                # keep visual scale at or above 1.0; no shrink
                self.target_scale = max(self.target_scale, 1.0)

    def update(self, dt):
        # smooth interpolation towards target_scale
        speed = 8.0
        diff = self.target_scale - self.scale
        if abs(diff) > 0.0001:
            self.scale += diff * min(1.0, speed * dt)
        else:
            self.scale = self.target_scale

    def draw(self, screen):
        # If an image has been provided (set by Game), use it and respect hover state.
        img = getattr(self, "_ball_hover_img", None) if self.hovered else getattr(self, "_ball_img", None)
        if img:
            r = int(self.radius * self.scale)
            size = (r * 2, r * 2)
            key = (id(img), size[0], size[1])
            surf = self._scaled_cache.get(key)
            if surf is None:
                try:
                    surf = pygame.transform.smoothscale(img, size)
                except Exception:
                    try:
                        surf = pygame.transform.scale(img, size)
                    except Exception:
                        surf = img
                self._scaled_cache[key] = surf
            rect = surf.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(surf, rect)
            return

        r = int(self.radius * self.scale)
        pygame.draw.circle(screen, (255, 225, 25), (int(self.x), int(self.y)), r)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), r, 3)
        # seam arcs (very simple)
        pygame.draw.arc(screen, (255, 255, 255), (self.x - r, self.y - r, r * 2, r * 2), 0.5, 2.6, 2)