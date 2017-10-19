import os
import pyglet
from pyglet import gl
import ctypes
import math

import jrti_game.data
from jrti_game.data import sprites
import jrti_game.flippable
from jrti_game.data import spritesheet_texture
from jrti_game.bug import Bug
from jrti_game.util import clamp
from jrti_game.state import state

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
    x=-400,
    y=-300,
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

    gl.glScalef(state.zoom, state.zoom, state.zoom)
    cx, cy = state.center
    gl.glTranslatef(-cx, -cy, 0)

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
        lx, ly = mouse_to_logical(x, y)
        main_screen.mouse_press(lx + 400, ly + 300, zoom=state.zoom)
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
        cx, cy = state.center
        state.center = cx + (px - x) / state.zoom, cy + (py - y) / state.zoom
        fix_box()
        state.last_drag_pos = x, y
    else:
        lx, ly = mouse_to_logical(x, y)
        main_screen.mouse_drag(lx + 400, ly + 300, zoom=state.zoom)
    state.last_mouse_pos = x, y


@window.event
def on_mouse_release(x, y, button, mod):
    state.alt_zoom_start = None
    state.last_drag_pos = None
    main_screen.mouse_release()


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    zoom(scroll_y, x, y)
    main_screen.mouse_release()


def zoom(amount, x, y):
    state.target_zoom = clamp(state.target_zoom * 1.1 ** amount, 1, 600**6)

def _zoom(amount):
    cx, cy = state.center
    lx, ly = mouse_to_logical(*state.last_mouse_pos)

    old = state.zoom
    state.zoom = amount

    cx = lx - (lx - cx) * old / state.zoom
    cy = ly - (ly - cy) * old / state.zoom
    state.center = cx, cy

    fix_box()

def fix_box():
    cx, cy = state.center
    cx = clamp(cx, 400 - 400 * state.zoom, 400 * state.zoom - 400)
    cy = clamp(cy, 300 - 300 * state.zoom, 300 * state.zoom - 300)

    state.center = cx, cy


#-400 +400 / state.zoom = cx

#400 / state.zoom -400 = cx


def mouse_to_logical(mx, my):
    cx, cy = state.center
    lx = (mx - 400) / state.zoom + cx
    ly = (my - 300) / state.zoom + cy
    return lx, ly


def logical_to_mouse(lx, ly):
    cx, cy = state.center
    mx = (lx - cx) * state.zoom + 400
    my = (ly - cy) * state.zoom + 300

    return mx, my


@pyglet.clock.schedule
def tick(dt):
    state.time += dt
    if 0.999 < state.zoom / state.target_zoom < 1.001:
        _zoom(state.target_zoom)
    else:
        x1 = state.zoom
        x2 = state.target_zoom
        w2 = 1 - math.exp(-dt) ** (10)
        w1 = 1 - w2
        _zoom( (x1**w1 * x2**w2) ** (1/1))
    main_screen.tick(dt)

def main():
    pyglet.app.run()
