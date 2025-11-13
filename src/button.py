import pygame

class Button:
    def __init__(self, rect, text, callback, font):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.font = font
        self.hover = False
        self.pressed = False
        # cache for scaled images when this button uses image assets
        self._img_cache = {}

    def set_text(self, text):
        """Update button text dynamically."""
        self.text = text

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
        # If this button has an image assigned, draw the image (with hover variant and slight scale)
        img = getattr(self, "_img", None)
        if img:
            img_hover = getattr(self, "_img_hover", None)
            chosen = img_hover if (self.hover and img_hover is not None) else img
            # enlarge slightly on hover
            scale = 1.12 if self.hover else 1.0
            target_w = max(1, int(self.rect.w * scale))
            target_h = max(1, int(self.rect.h * scale))
            key = (id(chosen), target_w, target_h)
            surf = self._img_cache.get(key)
            if surf is None:
                try:
                    surf = pygame.transform.smoothscale(chosen, (target_w, target_h))
                except Exception:
                    try:
                        surf = pygame.transform.scale(chosen, (target_w, target_h))
                    except Exception:
                        surf = chosen
                self._img_cache[key] = surf
            rect = surf.get_rect(center=self.rect.center)
            screen.blit(surf, rect)
            return

        # fallback to default drawn button
        color = (200,200,200)
        if self.pressed:
            color = (160,160,160)
        elif self.hover:
            color = (220,220,220)
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        txt = self.font.render(self.text, True, (0,0,0))
        tw, th = txt.get_size()
        screen.blit(
            txt, 
            (
                self.rect.x + (self.rect.w - tw)//2, 
                self.rect.y + (self.rect.h - th)//2
                )
            )