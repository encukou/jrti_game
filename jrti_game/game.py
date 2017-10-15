import os
import pyglet
from pyglet import gl

import jrti_game.data
import jrti_game.flippable
from jrti_game.data import spritesheet_texture

window_style = getattr(
    pyglet.window.Window,
    'WINDOW_STYLE_' + os.environ.get('GAME_PYGLET_WINDOW_STYLE', 'DEFAULT'),
)

window = pyglet.window.Window(
    width=800,
    height=600,
    style=window_style,
)

spr = jrti_game.flippable.Letter('J', height=8*4)

@window.event
def on_draw():
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, jrti_game.data.spritesheet_texture.id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    spr.draw()


def main():
    pyglet.app.run()

