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
        self.previous_state = None  # track if we came from RUNNING (paused)
        self.ui = UIManager(screen)
        self.player = PlayerState()
        self.save_manager = SaveManager("saves/save_slot_1.json")
        self.shop = Shop(self.player)
        # center the clickable ball on the screen and make it a bit larger
        center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        self.clickable = ClickableArea(center, 110, self.player)
        self.shop.set_clickable(self.clickable)
        self.physics = PhysicsManager()
        self.unsaved_changes = False  # Track unsaved changes
        
        # calculate centered button positions (screen width = 1280)
        screen_width = self.screen.get_width()
        center_x = screen_width // 2
        start_y = 150
        button_spacing = 70
        
        # Start button is larger
        start_btn_width = 200
        start_btn_height = 60
        start_rect = (center_x - start_btn_width // 2, 
                      start_y, 
                      start_btn_width, 
                      start_btn_height)
        
        # Other buttons are standard size
        btn_width = 140
        btn_height = 40
        
        # register menu buttons (shown in MENU state)
        self.ui.add_button("start", start_rect, "Start", self.start_game)
        save_rect = (center_x - btn_width // 2, 
                     start_y + button_spacing + 30, 
                     btn_width, 
                     btn_height)
        self.ui.add_button("save", save_rect, "Save", self.save_game)
        load_rect = (center_x - btn_width // 2, 
                     start_y + button_spacing * 2 + 30, 
                     btn_width, 
                     btn_height)
        self.ui.add_button("load", load_rect, "Load", self.load_game)
        credits_rect = (center_x - btn_width // 2, 
                        start_y + button_spacing * 3 + 30, 
                        btn_width, 
                        btn_height)
        self.ui.add_button("credits", 
                           credits_rect, 
                           "Credits", 
                           self.show_credits)
        quit_rect = (center_x - btn_width // 2, 
                     start_y + button_spacing * 4 + 30, 
                     btn_width, 
                     btn_height)
        self.ui.add_button("quit", 
                           quit_rect, 
                           "Quit", 
                           self.quit_game)
        
        # register pause button (shown during RUNNING state) - top-left corner
        pause_rect = (10, 10, btn_width, btn_height)
        self.ui.add_button("pause", pause_rect, "Pause", self.pause_game)
        
        # register back button (shown during CREDITS state)
        back_rect = (10, 10, btn_width, btn_height)
        self.ui.add_button("back", back_rect, "Back", self.back_to_menu)
        
        # shop UI positions
        self.shop.set_ui_positions(900, 120)
        # initialize button visibility for MENU state
        self.ui.set_buttons_visible_for_state("MENU")

    def start_game(self):
        self.state = "RUNNING"
        self.previous_state = "RUNNING"
        self.ui.set_buttons_visible_for_state("RUNNING")

    def pause_game(self):
        self.previous_state = self.state
        self.state = "MENU"
        self.ui.set_buttons_visible_for_state("MENU")
        # change Start button to Resume if we came from RUNNING
        if self.previous_state == "RUNNING":
            self.ui.buttons["start"].set_text("Resume")

    def show_credits(self):
        self.state = "CREDITS"
        self.ui.set_buttons_visible_for_state("CREDITS")

    def back_to_menu(self):
        self.state = "MENU"
        self.ui.set_buttons_visible_for_state("MENU")

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
            # update clickable animation
            try:
                self.clickable.update(dt)
            except Exception as e:
                print("Clickable update error:", e)
        self.ui.update(dt)

    def _draw_background(self):
        """Draw background image or green court."""
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
            bg = pygame.transform.scale(self.background, 
                                        self.screen.get_size())
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((20, 110, 20))

    def _load_ball_images(self):
        """Load ball images (cached on first call)."""
        if not hasattr(self, "_ball_img_map"):
            self._ball_img_map = {}
            for i in range(1, 7):
                filename = "assets/ball.png" if i == 1 else f"assets/ball-{i}.png"
                try:
                    img = pygame.image.load(filename)
                    try:
                        self._ball_img_map[i] = img.convert_alpha()
                    except Exception:
                        self._ball_img_map[i] = img.convert()
                except Exception:
                    self._ball_img_map[i] = None

        if not hasattr(self, "_ball_hover_img_map"):
            # optional: try to load hover variants like ball-hover.png or ball-2-hover.png
            self._ball_hover_img_map = {}
            for i in range(1, 7):
                hfile = "assets/ball-hover.png" if i == 1 else f"assets/ball-{i}-hover.png"
                try:
                    himg = pygame.image.load(hfile)
                    try:
                        self._ball_hover_img_map[i] = himg.convert_alpha()
                    except Exception:
                        self._ball_hover_img_map[i] = himg.convert()
                except Exception:
                    self._ball_hover_img_map[i] = None

        if not hasattr(self, "_ball_scaled_cache"):
            self._ball_scaled_cache = {}

        # load pause button images (optional) and attach them to the pause button
        try:
            pause_btn = self.ui.buttons.get("pause")
            if pause_btn is not None and not hasattr(pause_btn, "_img"):
                try:
                    pimg = pygame.image.load("assets/pause-btn.png")
                    try:
                        pause_btn._img = pimg.convert_alpha()
                    except Exception:
                        pause_btn._img = pimg.convert()
                except Exception:
                    pause_btn._img = None
                # Use the same image for hover state as requested
                try:
                    pause_btn._img_hover = pause_btn._img
                except Exception:
                    pause_btn._img_hover = None
                # if we successfully loaded a pause image, resize the button rect to the image's native size
                try:
                    if pause_btn._img:
                        w, h = pause_btn._img.get_size()
                        # keep the button at top-left (10,10)
                        pause_btn.rect.width = w
                        pause_btn.rect.height = h
                        pause_btn.rect.topleft = (20, 20)
                except Exception:
                    pass
        except Exception:
            pass

    def _render_running_state(self):
        """Render game during RUNNING state: balls, shop, clickable, points."""
        self._load_ball_images()

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

            # determine approximate size
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

            # pick image: priority -> ball.img, then mapping by 'type_id' attribute, else fallback to default
            img = None
            if hasattr(ball, "img") and ball.img:
                img = ball.img
            else:
                # if BallEntity has a type_id (building id), try to use our loaded map
                type_id = getattr(ball, "type_id", None)
                if type_id is None:
                    # try to infer from radius / value? skip
                    type_id = None
                if type_id and hasattr(self, "_ball_img_map"):
                    img = self._ball_img_map.get(type_id)
                else:
                    # fallback to the first ball image
                    img = next(iter(self._ball_img_map.values())) if hasattr(self, "_ball_img_map") else None

            # if hovered, try hover variant
            if hovered:
                hover_img = None
                if hasattr(ball, "img_hover") and ball.img_hover:
                    hover_img = ball.img_hover
                elif hasattr(self, "_ball_hover_img_map") and type_id:
                    hover_img = self._ball_hover_img_map.get(type_id)
                if hover_img:
                    img = hover_img

            if img and pos:
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
                try:
                    ball.draw(self.screen)
                except Exception:
                    pass


        # draw shop panel (buildings on the right)
        self.shop.draw(self.screen)

                # pass a default ball image to clickable area (if available)
        try:
            if hasattr(self, "_ball_img_map"):
                # use first available ball image as default for clickable
                first_img = None
                for v in self._ball_img_map.values():
                    if v is not None:
                        first_img = v
                        break
                if first_img is not None:
                    self.clickable._ball_img = first_img
                # hover variant if available
                if hasattr(self, "_ball_hover_img_map"):
                    first_hover = None
                    for v in self._ball_hover_img_map.values():
                        if v is not None:
                            first_hover = v
                            break
                    if first_hover is not None:
                        self.clickable._ball_hover_img = first_hover
        except Exception:
            pass


        # draw clickable ball
        try:
            self.clickable.draw(self.screen)
        except Exception as e:
            print("Clickable draw error:", e)

        # draw click power below the ball
        font_small = pygame.font.SysFont(None, 24)
        click_power_txt = font_small.render(
            f"Click power: {self.player.click_power}", 
            True, 
            (255,255,255)
            )
        ball_y = self.clickable.y + int(
            self.clickable.radius * self.clickable.scale
            ) + 20
        self.screen.blit(
            click_power_txt, 
            (self.clickable.x - click_power_txt.get_width() // 2, 
            ball_y)
            )

        # draw points top-center
        font = pygame.font.SysFont(None, 36)
        txt = font.render(
            f"Points: {int(self.player.points)}", True, (255,255,255)
            )
        self.screen.blit(txt, (540, 20))

    def _render_menu_state(self):
        """Render menu state: background with darkening overlay."""
        # draw a semi-transparent dark overlay over the game
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

    def _render_credits_state(self):
        """Render credits state: background and credits text."""
        # draw a semi-transparent dark overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont(None, 36)
        title = font.render("Credits", True, (255,255,255))
        self.screen.blit(
            title, 
            (self.screen.get_width() // 2 - title.get_width() // 2, 50)
            )

        credits_text = "Tennis Clicker\nDeveloped with Pygame"
        small_font = pygame.font.SysFont(None, 24)
        y = 150
        for line in credits_text.split("\n"):
            txt = small_font.render(line, True, (255,255,255))
            self.screen.blit(
                txt, 
                (self.screen.get_width() // 2 - txt.get_width() // 2, y)
                )
            y += 40

    def render(self):
        """Main render method: 
        draw background, 
        game state content, 
        then overlay menu/credits."""
        self._draw_background()

        # always render the game state in the background
        self._render_running_state()

        # if paused or in credits, render overlay on top
        if self.state == "MENU":
            self._render_menu_state()
        elif self.state == "CREDITS":
            self._render_credits_state()

        # draw UI buttons (menu, pause, etc.)
        self.ui.draw(self.screen, self.player)

        pygame.display.flip()