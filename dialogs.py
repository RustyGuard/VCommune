import json
from random import randint
from typing import Optional

from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from constants import EVENT_UPDATE
from ui import UIScrollArea, UIButton, Anchor, UIPopup, UIElement, UILabel


class MessagesScroll(UIScrollArea):
    def __init__(self, *args, font=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages_count = 0
        if not font:
            font = Font('assets/fonts/arial.ttf', 20)
        self.font = font

    def add_message(self, msg, from_me=False):
        self.messages_count += 1
        self.min_offset = -25 * self.messages_count
        self.max_offset = max(
            25 * self.messages_count - self.relative_bounds.height + self.min_offset,
            self.min_offset)
        self.max_offset = self.min_offset + max(
            25 * self.messages_count - self.relative_bounds.height, 0)

        anchor = Anchor.BOTTOM_RIGHT if from_me else Anchor.BOTTOM_LEFT
        self.append_child(
            UILabel(Rect(0, self.messages_count * 25, -5, 0), Color('black'), self.font, msg,
                    absolute_anchor=anchor,
                    relative_anchor=anchor))
        if self.offset - self.min_offset <= 25:
            self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.offset = self.min_offset


class DialogWindow(UIElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open('assets/dialogs.json') as json_file:
            self.dialogs = json.load(json_file)

        self.current_dialog: Optional[dict] = None
        self.current_dialog_name = None
        self.message_delay = 45

        self.message_queue = []
        self.timer = self.message_delay
        self.responses = UIElement(Rect(0, 0, 0, 0), None,
                                   absolute_anchor=Anchor.BOTTOM_RIGHT,
                                   relative_anchor=Anchor.BOTTOM_RIGHT)
        self.append_child(self.responses)

        self.messages_count = 0
        self.messages_container = MessagesScroll(Rect(0, 10, self.relative_bounds.w * 0.99, self.relative_bounds.h * 0.9), Color('beige'),
                                                 absolute_anchor=Anchor.TOP_CENTER,
                                                 relative_anchor=Anchor.TOP_CENTER,
                                                 max_offset=0)
        self.append_child(self.messages_container)

        self.on_dialog_started('initial')

    def on_dialog_started(self, name: str):
        self.current_dialog = self.dialogs[name]
        self.current_dialog_name = name
        self.responses.clear_children()
        if messages := self.current_dialog.get('messages', None):
            for msg in messages:
                self.message_queue.append((msg, False))
        else:
            self.on_dialog_ended()

    def on_dialog_ended(self):
        if delay_after := self.current_dialog.get('delay_after', None):
            self.timer += delay_after

        if next_dialog := self.current_dialog.get('next', None):
            self.on_dialog_started(next_dialog)
            return

        if response := self.current_dialog.get('responses', None):
            self.current_dialog = None
            self.current_dialog_name = None
            self.show_response_buttons(response)
            return

    def response(self, btn, dialog_name):
        for msg in dialog_name.get('messages', [btn.text]):
            self.message_queue.append((msg, True))

        self.on_dialog_started(dialog_name['next'])

        self.messages_container.scroll_to_bottom()

    def update(self, event):
        if event.type == EVENT_UPDATE:
            if not self.message_queue or not self.current_dialog:
                return

            self.timer -= 1
            if self.timer > 0:
                return

            self.timer = self.message_delay

            self.messages_container.add_message(*self.message_queue.pop(0))
            print(self.current_dialog)
            if not self.message_queue:
                self.on_dialog_ended()

        super().update(event)

    def show_response_buttons(self, buttons: dict):
        for i, (button_text, dialog_name) in enumerate(buttons.items()):
            print(button_text, dialog_name)

            btn = UIButton(Rect(-5 - i * 150, -5, 145, 25), Color('blue'), self.response,
                           dialog_name,
                           relative_anchor=Anchor.BOTTOM_RIGHT,
                           absolute_anchor=Anchor.BOTTOM_RIGHT,
                           text=button_text, text_color=Color('black'))

            self.responses.append_child(btn)
