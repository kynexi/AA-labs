# display.py
import pygame
from math import ceil
from time import time
from abc import ABC, abstractmethod


class Window:
    def __init__(self, screen):
        self.screen = screen
        self.widgets = {}

    def add_widget(self, widget_id, widget):
        self.widgets[widget_id] = widget

    def get_widget_value(self, widget_id):
        if widget_id not in self.widgets:
            return None
        return self.widgets[widget_id].get_value()

    def set_widget_value(self, widget_id, value):
        if widget_id not in self.widgets:
            return None
        return self.widgets[widget_id].set_value(value)

    def render(self):
        for widget in self.widgets.values():
            widget.render(self.screen)

    def update(self, event):
        for widget in self.widgets.values():
            widget.update(event)


class Box:
    def __init__(self, rect):
        self.isActive = False
        self.rect = pygame.Rect(rect)

    def update(self, event):
        self.mousePos = pygame.mouse.get_pos()
        self.clicked = event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(self.mousePos)
        self.hovered = self.rect.collidepoint(self.mousePos)


class InputBox(ABC, Box):
    def __init__(self, rect, label, color, font):
        super().__init__(rect)
        self.label = label
        self.color = color
        self.font = font

    def render(self, screen):
        label = self.font.render(self.label, True, self.color)
        screen.blit(label, (self.rect.x + (self.rect.w - label.get_width()) / 2, self.rect.y - 26))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def set_value(self, value):
        pass


class TextBox(InputBox):
    def __init__(self, rect, label, color, font, text):
        super().__init__(rect, label, color, font)
        self.text = text

    def render(self, screen):
        super().render(screen)
        surface = self.font.render(self.text, True, self.color)
        screen.blit(surface, surface.get_rect(center=self.rect.center))

    def update(self, event):
        super().update(event)
        if self.hovered and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit():
                self.text += event.unicode

    def get_value(self):
        return self.text

    def set_value(self, value):
        self.text = value


class SlideBox(InputBox):
    def __init__(self, rect, label, color, font):
        super().__init__(rect, label, color, font)
        self.start = self.rect.x + 6
        self.end = self.rect.x + self.rect.w - 6
        self.value = self.start
        self.dragging = False

    def render(self, screen):
        super().render(screen)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        pygame.draw.line(screen, self.color, (self.start, self.rect.y + 25), (self.end, self.rect.y + 25), 2)
        pygame.draw.line(screen, self.color, (self.value, self.rect.y + 5), (self.value, self.rect.y + 45), 12)

    def update(self, event):
        super().update(event)
        self.start = self.rect.x + 6
        self.end = self.rect.x + self.rect.w - 6

        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(self.mousePos):
            if self.start <= self.mousePos[0] <= self.end:
                self.dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if self.dragging:
            self.value = min(max(self.mousePos[0], self.start), self.end)

    def get_value(self):
        normalized_value = (self.value - self.start) / (self.end - self.start)
        return normalized_value

    def set_value(self, value):
        self.value = self.start + value * (self.end - self.start)


class ButtonBox(Box):
    def __init__(self, rect, inactive_img_path, active_img_path):
        super().__init__(rect)
        self.inactive_img = pygame.image.load(inactive_img_path)
        self.inactive_img = pygame.transform.scale(self.inactive_img, (rect[2], rect[3]))
        self.active_img = pygame.image.load(active_img_path)
        self.active_img = pygame.transform.scale(self.active_img, (rect[2], rect[3]))
        self.active = False

    def render(self, screen):
        img = self.active_img if self.active else self.inactive_img
        screen.blit(img, (self.rect.x, self.rect.y))

    def update(self, event):
        super().update(event)
        if self.clicked:
            self.active = not self.active

    def get_value(self):
        return self.active

    def set_value(self, value):
        self.active = value


class TextButtonBox(Box):
    """A text-labeled button (used when no image asset is available)."""

    def __init__(self, rect, label, color, font, bg_color=(40, 40, 40), active_bg=(80, 140, 90)):
        super().__init__(rect)
        self.label = label
        self.color = color
        self.font = font
        self.bg_color = bg_color
        self.active_bg = active_bg
        self.active = False

    def render(self, screen):
        bg = self.active_bg if self.active else self.bg_color
        pygame.draw.rect(screen, bg, self.rect)
        pygame.draw.rect(screen, self.color, self.rect, 2)
        text_surface = self.font.render(self.label, True, self.color)
        screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))

    def update(self, event):
        super().update(event)
        if self.clicked:
            self.active = not self.active

    def get_value(self):
        return self.active

    def set_value(self, value):
        self.active = value


class DropdownBox(InputBox):

    VISIBLE_OPTIONS = 8

    def __init__(self, rect, label, color, font, options, options_background_color):
        super().__init__(rect, label, color, font)
        self.openDropdown = False
        self.options = options
        self.options_background_color = options_background_color

        visible_count = min(len(options), self.VISIBLE_OPTIONS)
        self.dropdown_rect = pygame.Rect(
            self.rect.x,
            self.rect.y - self.rect.height * visible_count,
            self.rect.width,
            self.rect.height * visible_count
        )
        self.scroll_offset = 0
        self.selected_option = 0

    def render(self, screen):
        super().render(screen)

        option_text = self.font.render(self.options[self.selected_option], 1, self.color)
        screen.blit(option_text, option_text.get_rect(center=self.rect.center))

        if self.openDropdown:
            pygame.draw.rect(screen, self.options_background_color, self.dropdown_rect)
            pygame.draw.rect(screen, self.color, self.dropdown_rect, 2)

            for index in range(len(self.options)):
                rect = self.rect.copy()
                rect.y = self.rect.y - (index + 1) * self.rect.height

                pygame.draw.rect(screen, self.options_background_color, rect)
                pygame.draw.rect(screen, self.color, rect, 1)
                option_text = self.font.render(self.options[index], 1, self.color)
                screen.blit(option_text, option_text.get_rect(center=rect.center))

    def update(self, event):
        super().update(event)

        if self.clicked:
            self.openDropdown = not self.openDropdown

        self.handle_option_selection(event)

    def handle_option_selection(self, event):
        if not self.openDropdown:
            return
        for index in range(len(self.options)):
            rect = self.rect.copy()
            rect.y = self.rect.y - (index + 1) * self.rect.height

            if rect.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.selected_option = index
                self.openDropdown = False

    def get_value(self):
        return self.options[self.selected_option]

    def set_value(self, value):
        if isinstance(value, int):
            self.selected_option = value
        else:
            if value in self.options:
                self.selected_option = self.options.index(value)
