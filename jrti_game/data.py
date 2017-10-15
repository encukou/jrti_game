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
