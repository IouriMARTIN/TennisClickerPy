import pygame
from game import Game

pygame.init()
screen = pygame.display.set_mode((1280,720))
game = Game(screen)
game.start_game()
print('points before:', game.player.points)
evt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (640,280), 
                                                  'button': 1})
pygame.event.post(evt)
game.handle_events()
game.update(1/60.0)
print('points after:', game.player.points)
pygame.quit()
