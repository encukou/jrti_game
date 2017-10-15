import os
import pyglet

import jrti_game.data
import jrti_game.flippable

window_style = getattr(
    pyglet.window.Window,
    'WINDOW_STYLE_' + os.environ.get('GAME_PYGLET_WINDOW_STYLE', 'DEFAULT'),
)

window = pyglet.window.Window(
    width=800,
    height=600,
    style=window_style,
)

spr = jrti_game.flippable.Sprite()

@window.event
def on_draw():
    spr.draw()


def main():
    pyglet.app.run()

