from enum import Enum
from typing import Optional, Callable

import pygame
from pygame import Color, MOUSEWHEEL, mouse
from pygame.font import Font
from pygame.rect import Rect
from pygame.time import Clock

from constants import EVENT_SEC, EVENT_UPDATE


class Anchor(Enum):
    TOP_LEFT = 'TOP_LEFT'
    TOP_RIGHT = 'TOP_RIGHT'
    TOP_CENTER = 'TOP_CENTER'
    BOTTOM_LEFT = 'BOTTOM_LEFT'
    BOTTOM_RIGHT = 'BOTTOM_RIGHT'
    BOTTOM_CENTER = 'BOTTOM_CENTER'
    CENTER_LEFT = 'CENTER_LEFT'
    CENTER_RIGHT = 'CENTER_RIGHT'
    CENTER = 'CENTER'

    @property
    def horizontal_left(self):
        return self in (Anchor.CENTER_LEFT, Anchor.TOP_LEFT, Anchor.BOTTOM_LEFT)

    @property
    def horizontal_right(self):
        return self in (Anchor.CENTER_RIGHT, Anchor.TOP_RIGHT, Anchor.BOTTOM_RIGHT)

    @property
    def horizontal_center(self):
        return self in (Anchor.CENTER, Anchor.TOP_CENTER, Anchor.BOTTOM_CENTER)

    @property
    def vertical_top(self):
        return self in (Anchor.TOP_LEFT, Anchor.TOP_RIGHT, Anchor.TOP_CENTER)

    @property
    def vertical_bottom(self):
        return self in (Anchor.BOTTOM_LEFT, Anchor.BOTTOM_RIGHT, Anchor.BOTTOM_CENTER)

    @property
    def vertical_center(self):
        return self in (Anchor.CENTER_LEFT, Anchor.CENTER_RIGHT, Anchor.CENTER)


class UIElement:
    def __init__(self, bounds: Rect, color: Optional[Color],
                 absolute_anchor: Anchor = Anchor.TOP_LEFT, relative_anchor: Anchor = Anchor.TOP_LEFT):
        """

        :param bounds: Bounds of element relatively to parent element
        :param color: Main color of element
        :param absolute_anchor: Anchor of location at the point of the parent element
        :param relative_anchor:Anchor of point of (x, y) = (0, 0) on element
        """
        self.relative_bounds = bounds
        self.absolute_anchor = absolute_anchor
        self.relative_anchor = relative_anchor
        self.absolute_bounds = bounds.copy()
        self.color = color
        self.childs = []
        self.enabled = True
        self.parent = None

    def update_bounds(self):
        self.absolute_bounds = self.relative_bounds.copy()

        self.absolute_bounds.x = self.absolute_x
        self.absolute_bounds.y = self.absolute_y

        for child in self.childs:
            child.update_bounds()

    def clear_children(self):
        self.childs.clear()

    @property
    def absolute_x(self):
        if self.parent is None:
            return self.relative_bounds.x

        if self.absolute_anchor.horizontal_left:
            absolute_offset = self.parent.absolute_bounds.x
        elif self.absolute_anchor.horizontal_center:
            absolute_offset = self.parent.absolute_bounds.x + self.parent.relative_bounds.width / 2
        elif self.absolute_anchor.horizontal_right:
            absolute_offset = self.parent.absolute_bounds.x + self.parent.relative_bounds.width
        else:
            raise ValueError('Invalid absolute anchor')

        if self.relative_anchor.horizontal_left:
            relative_offset = 0
        elif self.relative_anchor.horizontal_center:
            relative_offset = - self.relative_bounds.width / 2
        elif self.relative_anchor.horizontal_right:
            relative_offset = - self.relative_bounds.width
        else:
            raise ValueError('Invalid relative anchor')

        return self.relative_bounds.x + absolute_offset + relative_offset

    @property
    def absolute_y(self):
        if self.parent is None:
            return self.relative_bounds.y

        if self.absolute_anchor.vertical_top:
            absolute_offset = self.parent.absolute_bounds.y
        elif self.absolute_anchor.vertical_center:
            absolute_offset = self.parent.absolute_bounds.y + self.parent.relative_bounds.height / 2
        elif self.absolute_anchor.vertical_bottom:
            absolute_offset = self.parent.absolute_bounds.y + self.parent.relative_bounds.height
        else:
            raise ValueError('Invalid absolute anchor')

        if self.relative_anchor.vertical_top:
            relative_offset = 0
        elif self.relative_anchor.vertical_center:
            relative_offset = - self.relative_bounds.height / 2
        elif self.relative_anchor.vertical_bottom:
            relative_offset = - self.relative_bounds.height
        else:
            raise ValueError('Invalid relative anchor')

        return self.relative_bounds.y + absolute_offset + relative_offset

    def move(self, x, y):
        self.relative_bounds.move_ip(x, y)
        self.update_bounds()

    def update(self, event):
        for elem in self.childs:
            if elem.enabled and elem.update(event):
                return True
        return False

    def render(self, screen):
        self.draw(screen)
        for elem in reversed(self.childs):
            if elem.enabled:
                elem.render(screen)

    def draw(self, screen):
        if self.color is not None:
            pygame.draw.rect(screen, self.color, self.absolute_bounds)

    def append_child(self, child):
        self.childs.append(child)
        child.parent = self
        child.update_bounds()

    def shutdown(self):
        pass


class MainLoop:
    def __init__(self, main_element: UIElement, screen):
        self.main_element = main_element
        self.screen = screen

    @property
    def main_element(self):
        return self._main_element

    @main_element.setter
    def main_element(self, value):
        self._main_element = value
        value.main = self

    def loop(self):
        clock = Clock()

        running = True

        pygame.time.set_timer(EVENT_UPDATE, 1000 // 60)
        pygame.time.set_timer(EVENT_SEC, 1000 // 1)

        while running:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    print('Exit')
                    self.main_element.shutdown()
                    print('Shutdowned')
                    return
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        print('Exit')
                        self.main_element.shutdown()
                        print('Shutdowned')
                        return

                self.main_element.update(event)

            self.screen.fill((0, 0, 0))
            self.main_element.render(self.screen)

            pygame.display.flip()
            clock.tick(60)


class UILabel(UIElement):
    def __init__(self, bounds: Rect, color: Color, font: Font, text: str,
                 absolute_anchor: Anchor = Anchor.TOP_LEFT, relative_anchor: Anchor = Anchor.TOP_LEFT):
        super().__init__(bounds, color, absolute_anchor, relative_anchor)
        self.font = font
        self.text = text
        self.text_image = self.font.render(self.text, True, self.color)
        self.relative_bounds.size = self.text_image.get_size()

    def update_text(self):
        self.text_image = self.font.render(self.text, True, self.color)

    def set_text(self, text: str):
        if self.text != text:
            self.text = text
            self.update_text()

    def set_color(self, color: Color):
        if self.color != color:
            self.color = color
            self.update_text()

    def draw(self, screen):
        screen.blit(self.text_image, self.absolute_bounds)


class FPSCounter(UILabel):
    def __init__(self, bounds: Rect, font: Font, absolute_anchor: Anchor = Anchor.TOP_LEFT,
                 relative_anchor: Anchor = Anchor.TOP_LEFT):
        super().__init__(bounds, Color('green'), font, 'FPS: 00', absolute_anchor, relative_anchor)
        self.frames = 0

    def update(self, event):
        if event.type == EVENT_SEC:
            self.set_text(f'FPS: {self.frames}')
            self.frames = 0

        return super().update(event)

    def draw(self, screen):
        super().draw(screen)
        self.frames += 1


class UIImage(UIElement):
    def __init__(self, bounds, image_path, image=None, absolute_anchor: Anchor = Anchor.TOP_LEFT,
                 relative_anchor: Anchor = Anchor.TOP_LEFT):
        super().__init__(bounds, None, absolute_anchor, relative_anchor)
        self.image = pygame.image.load(image_path).convert() if (image_path is not None) else image
        if bounds.width != 0 and bounds.height != 0:
            self.image = pygame.transform.smoothscale(self.image, self.relative_bounds.size)

    def draw(self, screen):
        screen.blit(self.image, self.absolute_bounds.topleft)


class UIButton(UIElement):
    def __init__(self, bounds, color, callback_func, *func_args,
                 absolute_anchor: Anchor = Anchor.TOP_LEFT, relative_anchor: Anchor = Anchor.TOP_LEFT,
                 text: Optional[str] = None, text_color=Color('Black')):
        super().__init__(bounds, color, absolute_anchor, relative_anchor)
        self.callback_func: Callable = callback_func
        self.callback_args = func_args
        self.text = text

        if text:
            self.append_child(UILabel(Rect(0, 0, 0, 0),
                                      text_color, Font('assets/fonts/arial.ttf', 20), text,
                                      Anchor.CENTER,
                                      Anchor.CENTER))

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.absolute_bounds.collidepoint(*event.pos):
                self.callback_func(self, *self.callback_args)
                return True

        return super().update(event)


class UIPopup(UILabel):
    def __init__(self, bounds: Rect, color: Color, font: Font, text: str, lifetime: int,
                 absolute_anchor: Anchor = Anchor.TOP_LEFT, relative_anchor: Anchor = Anchor.TOP_LEFT, velocity=(0, 0)):
        super().__init__(bounds, color, font, text, absolute_anchor, relative_anchor)
        self.life_time = lifetime
        self.velocity = velocity

    def update(self, event):
        if event.type == EVENT_UPDATE:
            self.life_time -= 1
            self.absolute_bounds.move_ip(self.velocity)

            if self.life_time <= 0:
                self.parent.childs.remove(self)
                return
        super().update(event)


class UIScrollArea(UIElement):

    def __init__(self, *args, min_offset=0, max_offset=100, **kwargs):
        super().__init__(*args, **kwargs)
        self._offset = 0
        self.min_offset = min_offset
        self.max_offset = max_offset

    def render(self, screen):
        self.draw(screen)
        screen.set_clip(self.absolute_bounds)
        for elem in reversed(self.childs):
            if elem.enabled:
                elem.render(screen)
        screen.set_clip(None)

    def append_child(self, child):
        super().append_child(child)
        child.absolute_bounds.y += self.offset

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        if self.offset == value:
            return

        self._offset = value
        for child in self.childs:
            child.update_bounds()
            child.absolute_bounds.y += self._offset

    def move_offset(self, value):
        offset = self._offset + value
        offset = min(offset, self.max_offset)
        offset = max(offset, self.min_offset)
        self.offset = offset

    def update(self, event):
        if event.type == MOUSEWHEEL:
            if self.absolute_bounds.collidepoint(*mouse.get_pos()):
                self.move_offset(event.y * 5)

        super().update(event)
