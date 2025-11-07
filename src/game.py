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
        self.clickable = ClickableArea((640, 280), 80, self.player)
        self.physics = PhysicsManager()
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

    def load_game(self):
        data = self.save_manager.load()
        if not data:
            return
        self.player = PlayerState.from_dict(data.get("player", {}))
        self.shop.from_dict(data.get("shop", {}), self.physics)
        # rewire references in UI/shop
        self.shop.player = self.player
        self.clickable.player = self.player

    def quit_game(self):
        self.save_manager.save(self.player, self.shop)
        self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            self.ui.handle_event(event)
            if self.state == "RUNNING":
                self.clickable.handle_event(event)
                self.shop.handle_event(event)

    def update(self, dt):
        if self.state == "RUNNING":
            produced = self.shop.total_production_per_second() * dt
            self.player.points += produced * self.player.global_multiplier
            self.physics.update(dt, self.shop.ball_entities)
            self.shop.update(dt)
        self.ui.update(dt)

    def render(self):
        self.screen.fill((20, 110, 20))  # tennis-court green
        # draw clickable area (tennis ball)
        self.clickable.draw(self.screen)
        # draw bouncing balls
        for ball in self.shop.ball_entities:
            ball.draw(self.screen)
        # draw shop and UI
        self.shop.draw(self.screen)
        self.ui.draw(self.screen, self.player)
        # draw points top-center
        font = pygame.font.SysFont(None, 36)
        txt = font.render(f"Points: {int(self.player.points)}", True, (255,255,255))
        self.screen.blit(txt, (540, 20))
        pygame.display.flip()