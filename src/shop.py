# shop.py
import pygame
import random
from building import Building
from upgrade import Upgrade
from ball_entity import BallEntity

class Shop:
    def __init__(self, player, screen_width=1280, screen_height=720):
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height

        # ----- BUILDINGS -----
        self.buildings = {
            1: Building(1, "Ball Machine", base_price=50, count=0, production_per_second=0.5),
            2: Building(2, "Pro Launcher", base_price=300, count=0, production_per_second=4.0),
            3: Building(3, "Ball Factory", base_price=1500, count=0, production_per_second=15.0),
            4: Building(4, "Tennis Lab", base_price=8000, count=0, production_per_second=75.0),
            5: Building(5, "Quantum Server", base_price=50000, count=0, production_per_second=400.0),
            6: Building(6, "Tennis Paradox Core", base_price=300000, count=0, production_per_second=2500.0),
        }

        # ----- SEQUENTIAL UPGRADES -----
        self.upgrade_list = [
            Upgrade("up1", "Better Swing I", "x2 power, +15% size", price=200),
            Upgrade("up2", "Better Swing II", "x2 power, +15% size", price=2000),
            Upgrade("up3", "Better Swing III", "x2 power, +15% size", price=12000),
        ]
        self.current_upgrade_index = 0

        self.ball_entities = []

        # FONT
        self.font = pygame.font.SysFont(None, 32)
        self.font_small = pygame.font.SysFont(None, 20)

        # LOAD SHOP BG (350x700px)
        try:
            self.shop_bg = pygame.image.load("assets/shop-bg.png").convert_alpha()
        except:
            self.shop_bg = None

        # Create rect for positioning - use original size
        if self.shop_bg:
            self.shop_bg_rect = self.shop_bg.get_rect()
        else:
            self.shop_bg_rect = pygame.Rect(0, 0, 350, 700)

        # Position at top-right
        self.shop_bg_rect.right = self.screen_width - 20
        self.shop_bg_rect.top = 0

        # Initialize ui_x and ui_y for compatibility
        self.ui_x = self.shop_bg_rect.x
        self.ui_y = self.shop_bg_rect.y

        # BUILDING CARD IMAGES
        self.building_images = {}
        for i in self.buildings.keys():
            try:
                img = pygame.image.load(f"assets/shop-item-{i}.png").convert_alpha()
                img = pygame.transform.smoothscale(img, (260, 70))
            except:
                img = None
            self.building_images[i] = img

        # BALL IMAGES
        self.ball_images = {}
        for i in range(1, 7):
            filename = "assets/ball.png" if i == 1 else f"assets/ball-{i}.png"
            try:
                img = pygame.image.load(filename).convert_alpha()
            except:
                img = None
            self.ball_images[i] = img

        # Upgrade effect multipliers
        self.click_power_multiplier = 1.0
        self.clickable_scale_multiplier = 1.0

        self.clickable = None

    def set_ui_positions(self, x, y):
        """Defines where the shop UI panel is drawn."""
        self.ui_x = x
        self.ui_y = y
        # IMPORTANT: Also update shop_bg_rect position
        self.shop_bg_rect.x = x
        self.shop_bg_rect.y = y

    def set_ui_size(self, width, height):
        """Set UI dimensions."""
        self.ui_width = width
        self.ui_height = height

    def set_clickable(self, clickable):
        """Set reference to the clickable object."""
        self.clickable = clickable
        try:
            if hasattr(self.clickable, "scale"):
                self.clickable.scale = getattr(self.player, "clickable_scale", 1.0)
        except Exception:
            pass

    def handle_event(self, event):
        """Handle mouse clicks for purchasing buildings and upgrades."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # BUILDING CLICKS
            i = 0
            for bid, b in self.buildings.items():
                # Center cards in 350px wide background: (350 - 260) / 2 = 45px offset
                rect = pygame.Rect(
                    self.shop_bg_rect.x + 45,
                    self.shop_bg_rect.y + 150 + i * 75,
                    260,
                    70
                )
                if rect.collidepoint(mx, my):
                    self.attempt_buy_building(bid)
                i += 1

            # UPGRADE CLICK
            if self.current_upgrade_index < len(self.upgrade_list):
                up_rect = pygame.Rect(
                    self.shop_bg_rect.x + 75,
                    self.shop_bg_rect.y + 140 + len(self.buildings) * 75 + 10,
                    200,
                    60
                )
                if up_rect.collidepoint(mx, my):
                    self.attempt_buy_upgrade()

    def attempt_buy_building(self, building_id):
        """Attempt to purchase a building."""
        b = self.buildings.get(building_id)
        if not b:
            return
        price = b.price_next()
        if self.player.points >= price:
            self.player.points -= price
            b.count += 1
            self.spawn_balls_for_building(building_id, count=1)

    def spawn_balls_for_building(self, building_id, count=1):
        """Spawn ball entities for a building."""
        for _ in range(count):
            img = self.ball_images.get(building_id)
            x = random.uniform(200, 800)
            y = random.uniform(100, 600)
            vx = random.uniform(-200, 200)
            vy = random.uniform(-150, 150)

            b = self.buildings.get(building_id)
            value = getattr(b, "production_per_second", 1.0)
            radius = 12 + int(building_id * 2)

            be = BallEntity(x, y, vx, vy, radius=radius, value=value)
            try:
                be.img = img
            except Exception:
                pass
            try:
                be.type_id = int(building_id)
            except Exception:
                be.type_id = None
            self.ball_entities.append(be)

    def attempt_buy_upgrade(self):
        """Attempt to purchase the next sequential upgrade."""
        if self.current_upgrade_index >= len(self.upgrade_list):
            return

        u = self.upgrade_list[self.current_upgrade_index]

        if self.player.points >= u.price:
            self.player.points -= u.price
            u.bought = True
            self.current_upgrade_index += 1
            self.recompute_upgrade_effects()

    def recompute_upgrade_effects(self):
        """Apply all purchased upgrade effects."""
        power_mult = 1.0
        size_mult = 1.0

        for up in self.upgrade_list:
            if up.bought:
                power_mult *= 2.0
                size_mult *= 1.15

        self.click_power_multiplier = power_mult
        self.clickable_scale_multiplier = size_mult

        # Apply to player
        try:
            base = getattr(self.player, "base_click_power", None)
            if base is None:
                self.player.base_click_power = getattr(self.player, "click_power", 1.0)
                base = self.player.base_click_power
            self.player.click_power = base * self.click_power_multiplier
        except Exception:
            pass

        # Apply to clickable
        try:
            if self.clickable is not None:
                if not hasattr(self.clickable, "base_scale"):
                    self.clickable.base_scale = getattr(self.clickable, "scale", 1.0)
                self.clickable.scale = getattr(self.clickable, "base_scale", 1.0) * self.clickable_scale_multiplier
        except Exception:
            pass

    def total_production_per_second(self):
        """Calculate total production from buildings and balls."""
        total = 0.0
        for b in self.buildings.values():
            total += b.production_per_second * b.count
        for ball in self.ball_entities:
            total += getattr(ball, "value", 0.0) * 0.2
        return total

    def update(self, dt):
        """Update shop state and ball entities."""
        self.recompute_upgrade_effects()

        # Auto restore missing balls if any vanished
        desired_ball_count = sum(b.count for b in self.buildings.values())
        while len(self.ball_entities) < desired_ball_count:
            owned = [bid for bid, b in self.buildings.items() if b.count > 0]
            if not owned:
                break
            bid = random.choice(owned)
            self.spawn_balls_for_building(bid, count=1)

        # Update all ball entities
        for ball in list(self.ball_entities):
            try:
                if hasattr(ball, "update"):
                    ball.update(dt)
            except Exception:
                pass

    def draw(self, screen):
        """Draw the shop UI."""
        # Shop background
        if self.shop_bg:
            screen.blit(self.shop_bg, self.shop_bg_rect)
        else:
            pygame.draw.rect(screen, (30, 30, 30), self.shop_bg_rect, border_radius=12)

        # BUILDING SLOTS
        i = 0
        for bid, b in self.buildings.items():
            # Center cards in 350px wide background: (350 - 260) / 2 = 45px offset
            rect = pygame.Rect(
                self.shop_bg_rect.x + 45,
                self.shop_bg_rect.y + 150 + i * 75,
                260,
                70
            )

            # Card background
            card = self.building_images.get(bid)
            if card:
                screen.blit(card, rect)
            else:
                pygame.draw.rect(screen, (60, 60, 60), rect, border_radius=8)

            # Name (centered)
            name_surf = self.font.render(b.name, True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(rect.centerx, rect.y + 20))
            screen.blit(name_surf, name_rect)

            # Price (bottom left)
            price = self.font.render(f"{b.price_next()}$", True, (255, 220, 100))
            screen.blit(price, (rect.x + 12, rect.bottom - 32))

            # Count (bottom right in brown)
            count = self.font.render(f"x{b.count}", True, (66, 43, 21))
            count_rect = count.get_rect(bottomright=(rect.right - 12, rect.bottom - 10))
            screen.blit(count, count_rect)

            i += 1

        # UPGRADE (only show current one)
        if self.current_upgrade_index < len(self.upgrade_list):
            u = self.upgrade_list[self.current_upgrade_index]

            rect = pygame.Rect(
                self.shop_bg_rect.x + 75,
                self.shop_bg_rect.y + 140 + len(self.buildings) * 75 + 10,
                200,
                60
            )

            pygame.draw.rect(screen, (80, 60, 120), rect, border_radius=10)

            # Name centered
            title = self.font.render(u.name, True, (255, 255, 255))
            trect = title.get_rect(center=(rect.centerx, rect.y + 20))
            screen.blit(title, trect)

            # Price bottom left
            price = self.font.render(f"{u.price}$", True, (255, 220, 100))
            screen.blit(price, (rect.x + 12, rect.bottom - 28))

    def to_dict(self):
        """Serialize shop state for saving."""
        return {
            "buildings": {k: v.to_dict() for k, v in self.buildings.items()},
            "current_upgrade_index": self.current_upgrade_index,
            "upgrade_list": [u.to_dict() for u in self.upgrade_list],
            "balls": [{
                "x": b.x,
                "y": b.y,
                "vx": b.vx,
                "vy": b.vy,
                "radius": b.radius,
                "value": b.value,
                "type_id": getattr(b, "type_id", None)
            } for b in self.ball_entities]
        }

    def from_dict(self, d, physics=None):
        """Load shop state from saved data."""
        bld = d.get("buildings", {})
        for k_str, v in bld.items():
            try:
                k = int(k_str)
            except Exception:
                k = k_str
            if k in self.buildings:
                self.buildings[k].count = v.get("count", 0)

        self.current_upgrade_index = d.get("current_upgrade_index", 0)
        
        ups = d.get("upgrade_list", [])
        for i, u_data in enumerate(ups):
            if i < len(self.upgrade_list):
                self.upgrade_list[i].bought = u_data.get("bought", False)

        self.ball_entities = []
        for bd in d.get("balls", []):
            be = BallEntity(
                bd.get("x", 400),
                bd.get("y", 300),
                bd.get("vx", 0),
                bd.get("vy", 0),
                radius=bd.get("radius", 12),
                value=bd.get("value", 1.0)
            )
            try:
                be.type_id = int(bd.get("type_id")) if bd.get("type_id") is not None else None
            except Exception:
                be.type_id = None
            # Attach image if possible
            try:
                if be.type_id and be.type_id in self.ball_images:
                    be.img = self.ball_images.get(be.type_id)
            except Exception:
                pass
            self.ball_entities.append(be)
        
        # Recompute effects after loading
        self.recompute_upgrade_effects()