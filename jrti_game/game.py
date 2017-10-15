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

letters = []
letters.extend(jrti_game.flippable.letters(
    "Just Read the",height=8*4, y=400 + 8*2, x=400, center=True))
letters.extend(jrti_game.flippable.letters(
    "Instructions!",height=8*8, y=400 - 8*8, x=400, center=True))
letters.extend(jrti_game.flippable.letters(
    "They're behind everything!", height=8*2, y=8*8, x=400, center=True))
letters.extend(jrti_game.flippable.letters(
    "PyWeek 24 entry", height=8, y=8*3, x=400, center=True))
letters.extend(jrti_game.flippable.letters(
    "https://pyweek.org/e/instructions/", height=8, y=8*1, x=400, center=True))

@window.event
def on_draw():
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, jrti_game.data.spritesheet_texture.id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    for letter in letters:
        letter.draw()


def main():
    pyglet.app.run()

