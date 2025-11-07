def update(self, dt, screen_rect):
    self.x += self.vx * dt
    self.y += self.vy * dt
    if self.y - self.radius < screen_rect.left:
        self.y = screen_rect.left + self.radius
        self.vy = -self.vy
    if self.y + self.radius > screen_rect.right:
        self.y = screen_rect.right - self.radius
        self.vy = -self.vy
    if self.x - self.radius < screen_rect.left:
        self.x = screen_rect.left + self.radius
        self.vx = -self.vx
    if self.x + self.radius > screen_rect.right:
        self.x = screen_rect.right - self.radius
        self.vx = -self.vx
