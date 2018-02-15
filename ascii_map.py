#!/usr/bin/env python

import os
from PIL import Image

PURPLE = '\033[95m'
BLUE = '\033[34m'
YELLOW = '\033[33m'
GREEN = '\033[32m'
RED = '\033[31m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
BLINK = '\033[5m'


def get_terminal_size():
    try:
        r, c = os.popen('stty size', 'r').read().split()
        rows, columns = int(r) - 1, int(c)
    except ValueError:
        rows, columns = 30, 120
    return columns, rows


class WorldMap:
    def __init__(self, width, height, chars=' -'):
        self.width = width
        self.height = height
        img = Image.open('world.bmp')
        pixels = self._normalize_colors([i for i in img.resize((width, height)).getdata()], len(chars))
        pixels = map(lambda x: chars[int(x)], pixels)
        self.dot_map = [pixels[(i * width):((i + 1) * width)] for i in range(height)]

    @staticmethod
    def _normalize_colors(pixel_list, color_count):
        pixels = map(sum, pixel_list)
        min_color = min(pixels)
        pixels = map(lambda x: x - min_color, pixels)
        max_color = max(pixels)
        return map(lambda x: (1.0 - x / max_color) * (color_count - 1), pixels)

    def add_point(self, coordinates, mark='X', style=UNDERLINE+RED):
        latitude = self.height * (77 - coordinates[0]) / 134
        longitude = self.width * (150 + coordinates[1]) / 332
        self.insert_msg(int(round(latitude)), int(round(longitude)), mark, style)

    def add_text(self, list_of_strings):
        if len(list_of_strings) >= self.height - 1:
            list_of_strings = list_of_strings[-(self.height - 1):]
        for i, s in enumerate(reversed(list_of_strings)):
            self.insert_msg(self.height - 1 - i, 0, s)

    def insert_msg(self, row, column, string, style=''):
        self.dot_map[row][column: column + len(string)] = string
        if style:
            self.dot_map[row][column] = style + self.dot_map[row][column]
            self.dot_map[row][column + len(string) - 1] += ENDC

    def __str__(self):
        return "\n".join(("".join(r) for r in self.dot_map))


if __name__ == '__main__':
    import time
    dot_map = WorldMap(*get_terminal_size())
    print(dot_map)
    points = {'MO': (55.750, 37.617),
              'X': (0, 0),
              'LA': (37.419, -122.057),
              'BA': (-34, -58),
              'AU': (-27, 133),
              'SY': (-34, 151)}

    for city, coords in points.iteritems():
        time.sleep(1)
        dot_map.add_point(coords, city)
        print(dot_map)
