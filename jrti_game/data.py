import pyglet.image
import png

from pathlib import Path

data_path = Path(__file__).parent / 'data'

spritesheet_path = data_path / 'spritesheet.png'
spritesheet_image = pyglet.image.load(str(spritesheet_path))
spritesheet_texture = spritesheet_image.get_texture()
