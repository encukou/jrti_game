import os
import pyglet
from pyglet import gl
import ctypes
import types

import jrti_game.data
from jrti_game.data import sprites
import jrti_game.flippable
from jrti_game.data import spritesheet_texture
from jrti_game.bug import Bug

state = types.SimpleNamespace(
    zoom=1,
    alt_zoom_start=None,
    last_drag_pos=None,
    center=[400, 300],
    last_mouse_pos=(0, 0),
    time=0,
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


all(jrti_game.flippable.letters(
    "Just Read the", scale=4, y=8*36, x=300, center=True, parent=title_plaque))
all(jrti_game.flippable.letters(
    "Instructions!", scale=8, y=8*24, x=300, center=True, parent=title_plaque))

Bug(parent=title_plaque)

all(jrti_game.flippable.letters(
    "They're behind everything!", scale=2, y=8*8, x=400, center=True,
    parent=main_screen))
all(jrti_game.flippable.letters(
    "PyWeek 24 entry", scale=1, y=8*3, x=400, center=True,
    parent=main_screen))
all(jrti_game.flippable.letters(
    "https://pyweek.org/e/instructions/", scale=1, y=8*1, x=400, center=True,
    parent=main_screen))

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
    gl.glMatrixMode(gl.GL_MODELVIEW)


    gl.glLoadIdentity()
    gl.glTranslatef(-400*state.zoom, -300*state.zoom, 0)
    gl.glScalef(state.zoom, state.zoom, state.zoom)
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

    mx, my = mouse_to_logical(*state.last_mouse_pos)
    gl.glTranslatef(round(mx), round(my), 0)
    gl.glColor4f(0, 1, 1, 1/state.zoom)
    sprites['eye'].blit(-4.5, -4)

    gl.glLoadIdentity()
    gl.glTranslatef(*logical_to_mouse(0, 0), 0)
    sprites['ex'].blit(-4.5, -4)
    gl.glLoadIdentity()
    gl.glTranslatef(*logical_to_mouse(400, 300), 0)
    sprites['crosshair'].blit(-4.5, -4)

    if os.environ.get('GAME_DEBUG'):
        fps_display.draw()


@window.event
def on_mouse_motion(x, y, button, mod):
    state.last_mouse_pos = x, y


@window.event
def on_mouse_press(x, y, button, mod):
    main_screen.mouse_release()
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
        state.center[0] += (px - x) / state.zoom
        state.center[1] += (py - y) / state.zoom
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
    state.zoom *= 1.1 ** amount
    if state.zoom > 600**6:
        state.zoom = 600**6
    elif state.zoom < 1:
        state.zoom = 1


def mouse_to_logical(mx, my):
    cx, cy = state.center
    lx = (mx-400) / state.zoom + cx
    ly = (my-300) / state.zoom + cy
    return lx, ly


def logical_to_mouse(lx, ly):
    cx, cy = state.center
    mx = (lx - cx) * state.zoom
    my = (ly - cy) * state.zoom
    return mx, my


@pyglet.clock.schedule
def tick(dt):
    state.time += dt

def main():
    pyglet.app.run()

