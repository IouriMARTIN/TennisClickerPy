import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1000, 800))
clock = pygame.time.Clock()

while True:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
 
    pygame.display.flip()
    clock.tick(60)