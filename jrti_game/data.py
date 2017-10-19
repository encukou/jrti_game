import functools
import textwrap

import pyglet.image
import pyglet.font
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


@functools.lru_cache()
def letter_uvwh(character):
    number = ord(character)
    if number < ord(' '):
        number = 127
    u = 8 * ((number - ord(' ')) % 32)
    v = 8 * ((number - ord(' ')) // 32)
    for width in range(8, 0, -1):
        if any(spritesheet_data[v+7-i][u+width-1]
               for i in range(8)):
            break
    return u, v, width+1, 9


def text_width(string):
    width = 0
    last_char = None
    for character in string:
        u, v, w, h = letter_uvwh(character)
        width += w + kerns.get((last_char, character), 0)
    return width

kerns = {
    ('s', 't'): -1,
    ('/', '/'): -1,
}

pyglet.font.add_file(str(data_path / 'font' / 'Itim-Regular.ttf'))

instruction_font_name = "Itim"


def load_instructions():
    instruction_texts = {}

    with (data_path / 'instructions.txt').open() as f:
        current_text = []
        current_heading = ''

        def _load_instruction():
            text = textwrap.dedent(''.join(current_text)).strip()
            instruction_texts[current_heading] = text
            current_text.clear()

        for line in f:
            if line.startswith('#'):
                _load_instruction()
                current_heading = line[1:].strip()
            else:
                current_text.append(line)
        _load_instruction()
    return instruction_texts

instruction_texts = load_instructions()

def get_instruction_text(key):
    return instruction_texts.get(key, instruction_texts['None'])

sprites = {
    'eye': spritesheet_texture.get_region(0, 3*8, 9, 8),
    'crosshair': spritesheet_texture.get_region(10, 3*8, 8, 8),
    'ex': spritesheet_texture.get_region(18, 3*8, 8, 8),
    'bug': spritesheet_texture.get_region(28, 3*8+1, 11, 11),
    'bugleg': spritesheet_texture.get_region(40, 3*8+1, 7, 11),
    'grabby': spritesheet_texture.get_region(48, 3*8, 7, 11),
    'grabtooth': spritesheet_texture.get_region(56, 3*8, 7, 11),
    'key': spritesheet_texture.get_region(63, 3*8, 18, 10),
    'keyhole': spritesheet_texture.get_region(80, 3*8+1, 16, 32),
}

