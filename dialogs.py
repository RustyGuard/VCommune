import json
from random import randint
from typing import Optional

from pydantic import BaseModel
from pygame import Color
from pygame.font import Font
from pygame.rect import Rect

from constants import EVENT_UPDATE
from ui import UIScrollArea, UIButton, Anchor, UIPopup, UIElement, UILabel


class MessageModel(BaseModel):
    text: str
    delay_after: int = 0
    delay_before: int = 0
    right_side: bool = True
    color: str = 'black'


class DialogResponse(BaseModel):
    text: str
    messages: list[MessageModel] = []
    next_dialog: str = None
    button_color: str = 'cadetblue'
    text_color: str = 'black'


class DialogModel(BaseModel):
    name: str
    messages: list[MessageModel] = []
    next_dialog: str = None
    responses: list[DialogResponse] = []


class MessagesScroll(UIScrollArea):
    def __init__(self, *args, font=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages_count = 0
        if not font:
            font = Font('assets/fonts/arial.ttf', 20)
        self.font = font

    def add_message(self, msg: MessageModel):
        self.messages_count += 1
        self.min_offset = -25 * self.messages_count
        self.max_offset = max(
            25 * self.messages_count - self.relative_bounds.height + self.min_offset,
            self.min_offset)
        self.max_offset = self.min_offset + max(
            25 * self.messages_count - self.relative_bounds.height, 0)

        anchor = Anchor.BOTTOM_LEFT if msg.right_side else Anchor.BOTTOM_RIGHT
        self.append_child(
            UILabel(Rect(0, self.messages_count * 25, -5, 0), Color(msg.color), self.font, msg.text,
                    absolute_anchor=anchor,
                    relative_anchor=anchor))
        if self.offset - self.min_offset <= 25:
            self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.offset = self.min_offset


class DialogWindow(UIElement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dialogs = []
        with open('assets/dialogs.json') as json_file:
            for dialog_json in json.load(json_file):
                self.dialogs.append(DialogModel(**dialog_json))

        self.current_dialog: Optional[DialogModel] = None
        self.message_delay = 45

        self.message_queue = []
        self.timer = self.message_delay
        self.responses = UIElement(Rect(0, 0, 0, 0), None,
                                   absolute_anchor=Anchor.BOTTOM_RIGHT,
                                   relative_anchor=Anchor.BOTTOM_RIGHT)
        self.append_child(self.responses)

        self.messages_count = 0
        self.messages_container = MessagesScroll(
            Rect(0, 10, self.relative_bounds.w * 0.99, self.relative_bounds.h * 0.9), Color('beige'),
            absolute_anchor=Anchor.TOP_CENTER,
            relative_anchor=Anchor.TOP_CENTER,
            max_offset=0)
        self.append_child(self.messages_container)

        self.on_dialog_started('initial')

    def get_dialog(self, name: str) -> DialogModel:
        for dialog in self.dialogs:
            if dialog.name == name:
                return dialog
        raise ValueError(f'No dialog with name = {name}')

    @property
    def current_dialog_name(self):
        return self.current_dialog.name if self.current_dialog else None

    def on_dialog_started(self, name: str):
        self.current_dialog = self.get_dialog(name)
        self.responses.clear_children()
        if self.current_dialog.messages:
            for msg in self.current_dialog.messages:
                self.message_queue.append(msg)
        else:
            self.on_dialog_ended()

    def on_dialog_ended(self):
        if self.current_dialog.next_dialog:
            self.on_dialog_started(self.current_dialog.next_dialog)
            return

        if self.current_dialog.responses:
            self.show_response_buttons(self.current_dialog.responses)

        self.current_dialog = None

    def response(self, btn, dialog_name, messages):
        for msg in messages:
            self.message_queue.append(msg)

        self.on_dialog_started(dialog_name)

        self.messages_container.scroll_to_bottom()

    def update(self, event):
        if event.type == EVENT_UPDATE:
            if not self.message_queue or not self.current_dialog:
                return

            self.timer -= 1
            if self.timer > 0:
                return

            self.timer = self.message_delay

            self.messages_container.add_message(self.message_queue.pop(0))
            if not self.message_queue:
                self.on_dialog_ended()

        super().update(event)

    def show_response_buttons(self, responses: list[DialogResponse]):
        for i, response in enumerate(responses):
            btn = UIButton(Rect(-5 - i * 150, -5, 145, 25), Color(response.button_color), self.response,
                           response.next_dialog, response.messages,
                           relative_anchor=Anchor.BOTTOM_RIGHT,
                           absolute_anchor=Anchor.BOTTOM_RIGHT,
                           text=response.text, text_color=Color(response.text_color))

            self.responses.append_child(btn)
