import pygame
from ui_manager import UIManager
from player_state import PlayerState
from shop import Shop
from clickable_area import ClickableArea
from save_manager import SaveManager
from physics_manager import PhysicsManager

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.state = "MENU"  # MENU, RUNNING, CREDITS
        self.ui = UIManager(screen)
        self.player = PlayerState()
        self.save_manager = SaveManager("saves/save_slot_1.json")
        self.shop = Shop(self.player)
        # center the clickable ball on the screen and make it a bit larger
        center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        self.clickable = ClickableArea(center, 110, self.player)
        self.physics = PhysicsManager()
        self.unsaved_changes = False  # Track unsaved changes
        # register simple buttons
        self.ui.add_button("start", (50,50,140,40), "Start", self.start_game)
        self.ui.add_button("save", (50,100,140,40), "Save", self.save_game)
        self.ui.add_button("load", (50,150,140,40), "Load", self.load_game)
        self.ui.add_button("quit", (50,200,140,40), "Quit", self.quit_game)
        # shop UI positions
        self.shop.set_ui_positions(900, 120)

    def start_game(self):
        self.state = "RUNNING"

    def save_game(self):
        self.save_manager.save(self.player, self.shop)
        self.unsaved_changes = False

    def load_game(self):
        data = self.save_manager.load()
        if not data:
            return
        self.player = PlayerState.from_dict(data.get("player", {}))
        self.shop.from_dict(data.get("shop", {}), self.physics)
        # rewire references in UI/shop
        self.shop.player = self.player
        self.clickable.player = self.player
        self.unsaved_changes = False

    def quit_game(self):
        if self.unsaved_changes:
            self.save_manager.save(self.player, self.shop)
        self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            try:
                if event.type == pygame.QUIT:
                    self.quit_game()
                # route event to UI and game systems; protect against exceptions
                try:
                    self.ui.handle_event(event)
                except Exception as e:
                    print("UI event handler error:", e)

                if self.state == "RUNNING":
                    try:
                        self.clickable.handle_event(event)
                    except Exception as e:
                        print("Clickable handler error:", e)
                    try:
                        self.shop.handle_event(event)
                    except Exception as e:
                        print("Shop handler error:", e)
            except Exception as e:
                # catch-all to avoid crashing the main loop
                print("Unexpected error processing event:", e)

    def update(self, dt):
        if self.state == "RUNNING":
            try:
                produced = self.shop.total_production_per_second() * dt
                self.player.points += produced * self.player.global_multiplier
            except Exception as e:
                print("Error computing production:", e)
            try:
                self.physics.update(dt, self.shop.ball_entities)
            except Exception as e:
                print("Physics update error:", e)
            try:
                self.shop.update(dt)
            except Exception as e:
                print("Shop update error:", e)
            self.unsaved_changes = True  # Mark changes as unsaved when game updates
        self.ui.update(dt)

    def render(self):
        # draw background image if available, else fallback to court green
        if not hasattr(self, "background"):
            try:
                img = pygame.image.load("assets/background.png")
                try:
                    self.background = img.convert_alpha()
                except Exception:
                    self.background = img.convert()
            except Exception:
                self.background = None

        if self.background:
            bg = pygame.transform.scale(self.background, self.screen.get_size())
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((20, 110, 20))  # tennis-court green
        # draw clickable area (tennis ball) -- drawing moved below after loading images so clickable
        # can use the same `ball.png` / `ball-hover.png` images if available.
        # draw bouncing balls using images (ball.png / ball-hover.png when hovered)
        if not hasattr(self, "_ball_img"):
            try:
                img = pygame.image.load("assets/ball.png")
                try:
                    self._ball_img = img.convert_alpha()
                except Exception:
                    self._ball_img = img.convert()
            except Exception:
                self._ball_img = None
        if not hasattr(self, "_ball_hover_img"):
            try:
                img = pygame.image.load("assets/ball-hover.png")
                try:
                    self._ball_hover_img = img.convert_alpha()
                except Exception:
                    self._ball_hover_img = img.convert()
            except Exception:
                self._ball_hover_img = None

        if not hasattr(self, "_ball_scaled_cache"):
            self._ball_scaled_cache = {}

        for ball in self.shop.ball_entities:
            # determine position
            pos = None
            if hasattr(ball, "rect"):
                rect = ball.rect
                pos = (rect.centerx, rect.centery)
            elif hasattr(ball, "pos"):
                p = ball.pos
                if isinstance(p, (tuple, list)) and len(p) >= 2:
                    pos = (int(p[0]), int(p[1]))
                elif hasattr(p, "x") and hasattr(p, "y"):
                    pos = (int(p.x), int(p.y))
            elif hasattr(ball, "x") and hasattr(ball, "y"):
                pos = (int(ball.x), int(ball.y))

            # determine approximate size (prefer radius, fallback to rect or size)
            size = None
            if hasattr(ball, "radius"):
                r = getattr(ball, "radius")
                try:
                    size = (int(r * 2), int(r * 2))
                except Exception:
                    size = None
            elif hasattr(ball, "rect"):
                rect = ball.rect
                size = (rect.width, rect.height)
            elif hasattr(ball, "size"):
                s = ball.size
                try:
                    size = (int(s), int(s))
                except Exception:
                    size = None

            # determine hovered state
            hovered = False
            if hasattr(ball, "hovered"):
                hovered = bool(ball.hovered)
            elif hasattr(ball, "is_hovered"):
                try:
                    hovered = bool(ball.is_hovered())
                except Exception:
                    hovered = False

            img = self._ball_hover_img if hovered else self._ball_img

            if img and pos:
                # scale and cache image for this size
                surf = img
                if size:
                    key = (id(img), size[0], size[1])
                    if key not in self._ball_scaled_cache:
                        try:
                            self._ball_scaled_cache[key] = pygame.transform.smoothscale(img, size)
                        except Exception:
                            try:
                                self._ball_scaled_cache[key] = pygame.transform.scale(img, size)
                            except Exception:
                                self._ball_scaled_cache[key] = img
                    surf = self._ball_scaled_cache[key]
                rect = surf.get_rect(center=pos)
                self.screen.blit(surf, rect)
            else:
                # fallback to existing draw method if present
                try:
                    ball.draw(self.screen)
                except Exception:
                    pass
        # draw shop and UI
        self.shop.draw(self.screen)

        # pass loaded ball images to clickable area so it can draw with images and hover
        try:
            if hasattr(self, "_ball_img"):
                self.clickable._ball_img = self._ball_img
            if hasattr(self, "_ball_hover_img"):
                self.clickable._ball_hover_img = self._ball_hover_img
        except Exception:
            pass

        # now draw the clickable area (uses image if available)
        try:
            self.clickable.draw(self.screen)
        except Exception as e:
            print("Clickable draw error:", e)

        self.ui.draw(self.screen, self.player)
        # draw points top-center
        font = pygame.font.SysFont(None, 36)
        txt = font.render(f"Points: {int(self.player.points)}", True, (255,255,255))
        self.screen.blit(txt, (540, 20))
        pygame.display.flip()