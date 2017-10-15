import os
import pyglet
from pyglet import gl
import ctypes

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

main_screen = jrti_game.flippable.Layer(
    width=800,
    height=600,
)
title_plaque = jrti_game.flippable.Layer(
    parent=main_screen,
    x=400 - 600//2,
    y=400 - 8*32,
    width=600,
    height=8*48,
    instructions='main_plaque',
)


title_plaque.children.extend(jrti_game.flippable.letters(
    "Just Read the",height=8*4, y=8*36, x=300, center=True))
title_plaque.children.extend(jrti_game.flippable.letters(
    "Instructions!",height=8*8, y=8*24, x=300, center=True))

main_screen.children.extend(jrti_game.flippable.letters(
    "They're behind everything!", height=8*2, y=8*8, x=400, center=True))
main_screen.children.extend(jrti_game.flippable.letters(
    "PyWeek 24 entry", height=8, y=8*3, x=400, center=True))
main_screen.children.extend(jrti_game.flippable.letters(
    "https://pyweek.org/e/instructions/", height=8, y=8*1, x=400, center=True))

fps_display = pyglet.window.FPSDisplay(window)

@window.event
def on_draw():
    window.clear()
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadMatrixf((ctypes.c_float * 16)(
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 1,
        0, 0, 0, 1))
    gl.glScalef(2/window.width, 2/window.height, 1/2048)
    gl.glTranslatef(-800/2, -600/2, 0)
    gl.glMatrixMode(gl.GL_MODELVIEW)

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, jrti_game.data.spritesheet_texture.id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

    gl.glFrontFace(gl.GL_CCW)
    gl.glCullFace(gl.GL_BACK)
    gl.glDisable(gl.GL_CULL_FACE)

    main_screen.draw_outer()
    main_screen.draw_flipping()

    if os.environ.get('GAME_DEBUG'):
        fps_display.draw()


@window.event
def on_mouse_press(x, y, button, mod):
    main_screen.mouse_press(x, y)


@window.event
def on_mouse_drag(x, y, dx, dy, button, mod):
    main_screen.mouse_drag(x, y)


@window.event
def on_mouse_release(x, y, button, mod):
    main_screen.mouse_release()


@pyglet.clock.schedule
def tick(dt):
    pass

def main():
    pyglet.app.run()

