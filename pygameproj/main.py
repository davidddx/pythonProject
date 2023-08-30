import pygame, sys, os, pymunk;
import globals
from settings import *
from classes import *
from pytmx.util_pygame import load_pygame;
# print("Current Working Dir: ", os.getcwd())

#====================code after pygame.init() below=====================


pygame.init();

clock = pygame.time.Clock()
globals.screen = pygame.display.set_mode((screenwidth, screenheight));
globals.levelhandler = levelhandler()

running = true;
while running:
    clock.tick(30) # makes max fps 30
    print("fps: ", clock.get_fps()) # debug code used to test fps/performance
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit();

    globals.levelhandler.update();

    pygame.display.update();


