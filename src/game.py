import pygame
# from ui_manager import UIManager
from player_state import PlayerState
# from shop import Shop
# from clickable_area import ClickableArea
from save_manager import SaveManager
# from physics_manager import PhysicsManager

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"  # MENU, RUNNING, CREDITS
        # self.ui = UIManager(screen)
        self.player = PlayerState()
        self.save_manager = SaveManager("saves/save_slot_1.json")
        # self.shop = Shop(self.player)
        # self.clickable = ClickableArea((640, 360), 100, self.player)
        # self.physics = PhysicsManager()
        # load assets, fonts, etc.

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_manager.save(self.player, self.shop)
                self.running = False
            # self.ui.handle_event(event)
            # self.clickable.handle_event(event)
            # self.shop.handle_event(event)

    def update(self, dt):
        if self.state == "RUNNING":
            # production
            produced = self.shop.total_production_per_second() * dt
            self.player.points += produced * self.player.global_multiplier
            self.physics.update(dt)
            # update UI, animations
        # self.ui.update(dt)

    def render(self):
        self.screen.fill((20, 120, 20))  # tennis court green
        # self.clickable.draw(self.screen)
        # self.shop.draw(self.screen)
        # self.ui.draw(self.screen)
        pygame.display.flip()
