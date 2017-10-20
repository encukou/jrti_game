import textwrap
import pkgutil
from pathlib import Path
import tempfile

import pyglet.image
import pyglet.font
import png

import jrti_game

data_path = Path(jrti_game.__file__).parent / 'data'


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


instruction_texts = load_instructions()


def get_instruction_text(key):
    return instruction_texts.get(key, instruction_texts['None'])


sprites = {
    'square': spritesheet_texture.get_region(0, 0, 1, 1),
    'eye': spritesheet_texture.get_region(0, 3*8, 9, 8),
    'crosshair': spritesheet_texture.get_region(10, 3*8, 8, 8),
    'ex': spritesheet_texture.get_region(18, 3*8, 8, 8),
    'bug': spritesheet_texture.get_region(28, 3*8+1, 11, 11),
    'bugleg': spritesheet_texture.get_region(40, 3*8+1, 7, 11),
    'grabby': spritesheet_texture.get_region(48, 3*8, 7, 7),
    'grabshadow': spritesheet_texture.get_region(48, 4*8+1, 8, 8),
    'grabtooth': spritesheet_texture.get_region(56, 3*8, 7, 11),
    'key': spritesheet_texture.get_region(63, 3*8, 18, 10),
    'keyhole': spritesheet_texture.get_region(80, 3*8+1, 16, 32),
    'circ3': spritesheet_texture.get_region(96, 3*8+1, 23, 23),
}
