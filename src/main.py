import pygame
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Tennis Clicker")
    clock = pygame.time.Clock()

    game = Game(screen)

    while game.running:
        dt = clock.tick(60) / 1000.0
        game.handle_events()
        game.update(dt)
        game.render()
    pygame.quit()

if __name__ == "__main__":
    main()