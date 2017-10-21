import textwrap
import pkgutil
from pathlib import Path
import tempfile
import os

import pyglet.image
import pyglet.font
import png


def get_data(name):
    return pkgutil.get_data('jrti_game', str(Path('data') / name))


with tempfile.TemporaryDirectory() as tmp:
    tmp_path = Path(tmp)

    def unpack_file(name):
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(str(dest), 'wb') as f:
            f.write(get_data(name))
        return str(dest)

    spritesheet_filename = unpack_file('spritesheet.png')
    spritesheet_image = pyglet.image.load(spritesheet_filename)
    spritesheet_texture = spritesheet_image.get_texture()

    def _load_spritesheet():
        with open(spritesheet_filename, 'rb') as f:
            width, height, data, metadata = png.Reader(f).read()
            data = list(data)
            data.reverse()
        return data, metadata['palette']

    spritesheet_data, spritesheet_palette = _load_spritesheet()

    pyglet.font.add_file(unpack_file('font/Itim-Regular.ttf'))
    instruction_font_name = "Itim"


def load_instructions():
    instruction_texts = {}

    current_text = []
    current_heading = ''

    def _load_instruction():
        text = textwrap.dedent('\n'.join(current_text)).strip()
        instruction_texts[current_heading] = text
        current_text.clear()

    for line in get_data('instructions.txt').decode().splitlines():
        if line.startswith('#'):
            _load_instruction()
            current_heading = line[1:].strip()
        else:
            current_text.append(line)
    _load_instruction()

    return instruction_texts


sprites = {
    'square': spritesheet_texture.get_region(0, 0, 1, 1),
    'eye': spritesheet_texture.get_region(0, 3*8, 9, 8),
    'crosshair': spritesheet_texture.get_region(10, 3*8, 8, 8),
    'ex': spritesheet_texture.get_region(18, 3*8, 8, 8),
    'bug': spritesheet_texture.get_region(28, 3*8+1, 11, 11),
    'bugleg': spritesheet_texture.get_region(40, 3*8+1, 7, 11),
    'grabby': spritesheet_texture.get_region(48, 3*8, 7, 7),
    'grabshadow': spritesheet_texture.get_region(48, 4*8+1, 8, 8),
    'grabtooth': spritesheet_texture.get_region(56, 3*8, 7, 7),
    'key': spritesheet_texture.get_region(63, 3*8, 18, 8),
    'key_head': spritesheet_texture.get_region(63, 3*8, 9, 8),
    'keyhole': spritesheet_texture.get_region(80, 3*8+1, 16, 32),
    'circ3': spritesheet_texture.get_region(96, 3*8+1, 23, 23),
    'eye_big': spritesheet_texture.get_region(0, 4*8+1, 13, 13),
    'bug_o': spritesheet_texture.get_region(0, 6*8+1, 13, 13),
    'hint_a': spritesheet_texture.get_region(16, 6*8+1, 13, 13),
    'hint_b': spritesheet_texture.get_region(32, 6*8+1, 13, 13),
    'adjuster': spritesheet_texture.get_region(48, 4*8+1, 23, 23),
}

default_keymap = {
    'LEFT': 'View Left',
    'UP': 'View Up',
    'DOWN': 'View Down',
    'RIGHT': 'View Right',
    'ESCAPE': 'Exit',
    'X': 'Quit',
    'R': 'Reassign',
    'G': 'Grabby',
    'K': 'Key',
    'O': 'Zoom Out',
    'P': 'Zoom In',
    'W': 'Tool Up',
    'A': 'Tool Left',
    'S': 'Tool Down',
    'D': 'Tool Right',

    '_0': 'Zoom 0',
    '_1': 'Zoom 1',
    '_2': 'Zoom 2',
    '_3': 'Zoom 3',
    '_4': 'Zoom 4',
    '_5': 'Zoom 5',
    '_6': 'Zoom 6',
    '_7': 'Zoom 7',
    '_8': 'Zoom 8',
    '_9': 'Zoom 9',
}

if os.environ.get('GAME_DEBUG'):
    default_keymap['C'] = 'Cheat'
