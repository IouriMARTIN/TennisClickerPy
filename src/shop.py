import pygame, random
from building import Building
from upgrade import Upgrade
from ball_entity import BallEntity

class Shop:
    def __init__(self, player):
        self.player = player
        self.buildings = {
            "ball_launcher": Building("ball_launcher", 
                                      "Ball Launcher", 
                                      base_price=50, 
                                      count=0, 
                                      production_per_second=0.5),
            "racket_factory": Building("racket_factory", 
                                       "Racket Factory", 
                                       base_price=300, 
                                       count=0, 
                                       production_per_second=4.0),
            "color_ball_maker": Building("color_ball_maker", 
                                         "Color Ball Maker", 
                                         base_price=1200, 
                                         count=0, 
                                         production_per_second=12.0)
        }
        self.upgrades = {
            "click_up_1": Upgrade("click_up_1", 
                                  "Better Swing", 
                                  "Increase click power x2", 
                                  price=200, 
                                  bought=False)
        }
        self.ball_entities = []
        self.ui_x = 900
        self.ui_y = 120
        self.font = pygame.font.SysFont(None, 22)

    def set_ui_positions(self, x, y):
        self.ui_x = x
        self.ui_y = y

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # buy buildings if click over their area
            i = 0
            for b in self.buildings.values():
                rect = pygame.Rect(self.ui_x, self.ui_y + i*70, 260, 60)
                if rect.collidepoint(mx, my):
                    self.attempt_buy_building(b.id)
                i += 1

    def attempt_buy_building(self, building_id):
        b = self.buildings[building_id]
        price = b.price_next()
        if self.player.points >= price:
            self.player.points -= price
            b.count += 1
            # when buying a ball launcher spawn a ball
            if building_id == "ball_launcher":
                self.spawn_ball()
            elif building_id == "color_ball_maker":
                # spawn a stronger colored ball
                self.spawn_ball(value=5.0, radius=16)

    def spawn_ball(self, value=1.0, radius=12):
        screen_rect = pygame.Rect(0,0,1280,720)
        x = random.uniform(200, 800)
        y = random.uniform(100, 600)
        vx = random.uniform(-200, 200)
        vy = random.uniform(-150, 150)
        be = BallEntity(x,y,vx,vy,radius=radius,value=value)
        self.ball_entities.append(be)

    def total_production_per_second(self):
        total = 0.0
        for b in self.buildings.values():
            total += b.production_per_second * b.count
        # each ball entity also contributes a small passive amount (its value * 0.2)
        for ball in self.ball_entities:
            total += ball.value * 0.2
        return total

    def update(self, dt):
        # simple auto-buy visual cap: ensure ball count tracks building counts (optional)
        # remove too many balls if needed
        # Also check upgrades
        if self.upgrades["click_up_1"].bought:
            self.player.click_power = max(self.player.click_power, 2.0)

    def draw(self, screen):
        # draw shop panel
        pygame.draw.rect(screen, 
                         (40,40,40), 
                         (self.ui_x-10, 
                          self.ui_y-10, 300, 260), 
                          border_radius=8)
        i = 0
        for b in self.buildings.values():
            rect = pygame.Rect(self.ui_x, self.ui_y + i*70, 260, 60)
            pygame.draw.rect(screen, (100,100,100), rect, border_radius=6)
            name = f"{b.name} (x{b.count})"
            price = b.price_next()
            txt = self.font.render(name, True, (255,255,255))
            screen.blit(txt, (rect.x+8, rect.y+6))
            txt2 = self.font.render(f"Price: {price}", True, (255,255,255))
            screen.blit(txt2, (rect.x+8, rect.y+30))
            i += 1
        # upgrades
        uy = self.ui_y + i*70 + 10
        for u in self.upgrades.values():
            rect = pygame.Rect(self.ui_x, uy, 260, 40)
            pygame.draw.rect(screen, (80,80,120), rect, border_radius=6)
            txt = self.font.render(f"{u.name} - {u.price}", 
                                   True, 
                                   (255,255,255))
            screen.blit(txt, (rect.x+8, rect.y+8))
            uy += 50

    def to_dict(self):
        return {
            "buildings": {k: v.to_dict() for k,v in self.buildings.items()},
            "upgrades": {k: v.to_dict() for k,v in self.upgrades.items()},
            "balls": [{"x": b.x, 
                       "y": b.y, 
                       "vx": b.vx, 
                       "vy": b.vy, 
                       "radius": b.radius, 
                       "value": b.value} for b in self.ball_entities]
        }

    def from_dict(self, d, physics=None):
        bld = d.get("buildings", {})
        for k,v in bld.items():
            if k in self.buildings:
                self.buildings[k].count = v.get("count", 0)
        ups = d.get("upgrades", {})
        for k,v in ups.items():
            if k in self.upgrades:
                self.upgrades[k].bought = v.get("bought", False)
        self.ball_entities = []
        for bd in d.get("balls", []):
            be = BallEntity(bd.get("x",400), 
                            bd.get("y",300), 
                            bd.get("vx",0), 
                            bd.get("vy",0), 
                            radius=bd.get("radius",12), 
                            value=bd.get("value",1.0))
            self.ball_entities.append(be)