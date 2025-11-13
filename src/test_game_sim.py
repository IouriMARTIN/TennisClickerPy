import pygame
from game import Game

pygame.init()
screen = pygame.display.set_mode((1280,720))
game = Game(screen)
# ensure running state
game.start_game()
# initial points
print('points before:', game.player.points)
# simulate mouse click at clickable center
evt = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (640,280), 'button': 1})
pygame.event.post(evt)
# handle events
game.handle_events()
# update for one frame
game.update(1/60.0)
print('points after:', game.player.points)
pygame.quit()
