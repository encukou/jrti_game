import os
import pyglet
from pyglet import gl
import ctypes
import types

import jrti_game.data
import jrti_game.flippable
from jrti_game.data import spritesheet_texture

state = types.SimpleNamespace(
    zoom=1,
    alt_zoom_start=None,
    last_drag_pos=None,
    center=[400, 300],
    last_mouse_pos=(0, 0),
)

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
    margin=4,
)


title_plaque.children.extend(jrti_game.flippable.letters(
    "Just Read the", scale=4, y=8*36, x=300, center=True))
title_plaque.children.extend(jrti_game.flippable.letters(
    "Instructions!", scale=8, y=8*24, x=300, center=True))

main_screen.children.extend(jrti_game.flippable.letters(
    "They're behind everything!", scale=2, y=8*8, x=400, center=True))
main_screen.children.extend(jrti_game.flippable.letters(
    "PyWeek 24 entry", scale=1, y=8*3, x=400, center=True))
main_screen.children.extend(jrti_game.flippable.letters(
    "https://pyweek.org/e/instructions/", scale=1, y=8*1, x=400, center=True))

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
    gl.glScalef(2/window.width*state.zoom, 2/window.height*state.zoom, 1/2048)
    gl.glTranslatef(-400, -300, 0)
    gl.glMatrixMode(gl.GL_MODELVIEW)

    gl.glLoadIdentity()
    cx, cy = state.center
    gl.glTranslatef(400-cx, 300-cy, 0)

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, jrti_game.data.spritesheet_texture.id)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)

    gl.glFrontFace(gl.GL_CCW)
    gl.glCullFace(gl.GL_BACK)
    gl.glDisable(gl.GL_CULL_FACE)

    main_screen.draw_outer()
    main_screen.draw_flipping()

    if os.environ.get('GAME_DEBUG'):
        fps_display.draw()


@window.event
def on_mouse_motion(x, y, button, mod):
    state.last_mouse_pos = x, y


@window.event
def on_mouse_press(x, y, button, mod):
    if mod & pyglet.window.key.MOD_SHIFT:
        state.alt_zoom_start = [y, (x, y)]
        return
    if mod & pyglet.window.key.MOD_CTRL:
        button = pyglet.window.mouse.RIGHT
    if button == pyglet.window.mouse.LEFT:
        main_screen.mouse_press(*mouse_to_logical(x, y))
    else:
        state.last_drag_pos = x, y


@window.event
def on_mouse_drag(x, y, dx, dy, button, mod):
    if state.alt_zoom_start is not None:
        azs = state.alt_zoom_start
        zoom((y - azs[0]) / 2, *azs[1])
        state.alt_zoom_start[0] = y
    if state.last_drag_pos is not None:
        px, py = state.last_drag_pos
        x, y = mouse_to_logical(x, y)
        state.center[0] += px - x
        state.center[1] += py - y
        state.last_drag_pos = x, y
    else:
        main_screen.mouse_drag(*mouse_to_logical(x, y))
    state.last_mouse_pos = x, y


@window.event
def on_mouse_release(x, y, button, mod):
    state.alt_zoom_start = None
    state.last_drag_pos = None
    main_screen.mouse_release()


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    zoom(scroll_y, x, y)


def zoom(amount, x, y):
    x, y = mouse_to_logical(x, y)
    state.zoom *= 1.1 ** amount
    if state.zoom > 600**6:
        state.zoom = 600**6
    elif state.zoom < 1:
        state.zoom = 1


def mouse_to_logical(x, y):
    lx = x * state.zoom
    ly = y * state.zoom
    return lx, ly


@pyglet.clock.schedule
def tick(dt):
    pass

def main():
    pyglet.app.run()

