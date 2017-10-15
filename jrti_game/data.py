import functools

import pyglet.image
import png

from pathlib import Path

data_path = Path(__file__).parent / 'data'

spritesheet_path = data_path / 'spritesheet.png'
spritesheet_image = pyglet.image.load(str(spritesheet_path))
spritesheet_texture = spritesheet_image.get_texture()

def _load_spritesheet():
    with spritesheet_path.open('rb') as f:
        width, height, data, metadata = png.Reader(f).read()
        data = list(data)
        data.reverse()
    return data, metadata['palette']

spritesheet_data, spritesheet_palette = _load_spritesheet()

def _color(r, g, b):
    """Return increasing numbers in subsequent calls; check palette entries"""
    _color.i += 1
    expected = spritesheet_palette[_color.i]
    if expected != (r, g, b):
        raise AssertionError(f'Bad spritesheet palette: {expected} != {r, g, b}')
    return _color.i

_color.i = -1

BLACK = _color(0, 0, 0)
WHITE = _color(255, 255, 255)
RED = _color(255, 0, 0)


@functools.lru_cache()
def letter_uvwh(character):
    number = ord(character)
    if not (ord(' ') < number <= ord('~')):
        number = 127
    u = 8 * ((number - ord(' ')) % 32)
    v = 8 * ((number - ord(' ')) // 32)
    for width in range(8, 0, -1):
        if spritesheet_data[v+7][u+width-1] != RED:
            break
    return u, v, width, 8


def text_width(string):
    width = 0
    for character in string:
        u, v, w, h = letter_uvwh(character)
        width += w
    return width
