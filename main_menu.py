from random import randint
from typing import Optional

from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from dialogs import DialogWindow
from ui import UIElement, FPSCounter, UIButton, UIPopup, Anchor, UIImage


class MainMenu(UIElement):
    def __init__(self, rect: Rect, color: Optional[Color]):
        super().__init__(rect, color)

        self.main = None
        self.font = Font('assets/fonts/arial.ttf', 20)

        self.append_child(FPSCounter(Rect(0, 0, 0, 0), self.font,
                                     absolute_anchor=Anchor.TOP_RIGHT,
                                     relative_anchor=Anchor.TOP_RIGHT))

        self.append_child(DialogWindow(Rect(0, 57, 1750, 787), Color('azure'),
                                       relative_anchor=Anchor.TOP_CENTER,
                                       absolute_anchor=Anchor.TOP_CENTER))

        self.append_child(UIImage(self.absolute_bounds.copy(), 'assets/images/screen.png'))
