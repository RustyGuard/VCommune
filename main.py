import pygame
from pygame import Color
from pygame.rect import Rect
from pygame.time import Clock

from config import config
from constants import EVENT_SEC, EVENT_UPDATE
from main_menu import MainMenu
from ui import UIElement, MainLoop


def main():
    pygame.init()
    screen = pygame.display.set_mode(config['screen']['size'])

    elem = MainMenu(Rect((0, 0), config['screen']['size']), Color('white'))

    m = MainLoop(elem, screen)
    m.loop()


if __name__ == '__main__':
    main()
