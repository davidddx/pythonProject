import pygame, sys, os;
import globals
from settings import *
from classes import *
from pytmx.util_pygame import load_pygame;
# print("Current Working Dir: ", os.getcwd())

#====================code after pygame.init() below=====================


pygame.init();

clock = pygame.time.Clock();
globals.screen = pygame.display.set_mode((screenwidth, screenheight));
game = game();
globals.levelhandler = game.levelhandler

running = true;
while running:
    clock.tick(30) # makes max fps 30
    #print("fps: ", clock.get_fps()) #  debug code used to test fps/performance
    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit();
        sys.exit();
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();

    game.run();

    pygame.display.update();


