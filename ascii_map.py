#!/usr/bin/env python

import os
import numpy as np
from PIL import Image


def get_terminal_size():
    try:
        r, c = os.popen('stty size', 'r').read().split()
        rows, columns = int(r) - 1, int(c)
    except ValueError:
        rows, columns = 30, 120
    return columns, rows


class WorldMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        chars = np.asarray(list(' -'))
        img = Image.open('world.bmp')
        img = np.sum(np.asarray(img.resize((width, height))), axis=2)
        img -= img.min()
        img = (1.0 - img / img.max()) * (chars.size - 1)
        self.dot_map = chars[img.astype(int)]

    def add_point(self, coordinates, mark='X'):
        latitude = self.height * (78 - coordinates[0]) / 134
        longitude = self.width * (151 + coordinates[1]) / 330
        self.insert_line(int(round(latitude)), int(round(longitude)), mark)

    def add_text(self, list_of_strings):
        if len(list_of_strings) >= self.height - 1:
            list_of_strings = list_of_strings[-(self.height - 1):]
        for i, s in enumerate(reversed(list_of_strings)):
            self.insert_line(self.height - 1 - i, 0, s)

    def insert_line(self, row, column, string):
        for i, c in enumerate(string):
            self.dot_map[row, column + i] = c

    def __str__(self):
        return "\n".join(("".join(r) for r in self.dot_map))


if __name__ == '__main__':
    import time
    dot_map = WorldMap(*get_terminal_size())
    print dot_map
    points = {'MO': (55.750, 37.617),
              'X': (0, 0),
              'LA': (37.419, -122.057),
              'BA': (-34, -58),
              'AU': (-27, 133),
              'SY': (-34, 151)}

    for city, coords in points.iteritems():
        time.sleep(1)
        dot_map.add_point(coords, city)
        print dot_map
