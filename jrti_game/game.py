import os
import pyglet
from pyglet import gl
import ctypes
import math
import random

import jrti_game.data
from jrti_game.data import sprites
import jrti_game.flippable
from jrti_game.data import spritesheet_texture
from jrti_game.bug import BugArena
from jrti_game.util import clamp
from jrti_game.state import state
from jrti_game import tool

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
bug_arena = BugArena(
    parent=main_screen,
    x=400 - 600//2,
    y=400 - 8*32,
    width=600,
    height=8*48,
    instructions='main_plaque',
    margin=4,
)

all(jrti_game.flippable.letters(
    "Just Read the", scale=4, y=8*36, x=300, center=True, parent=bug_arena))
all(jrti_game.flippable.letters(
    "Instructions!", scale=8, y=8*24, x=300, center=True, parent=bug_arena))

for x in range(2):
    bug_arena.spawn_bug()

all(jrti_game.flippable.letters(
    "They're behind everything!", scale=2, y=8*8, x=400, center=True,
    parent=main_screen))
all(jrti_game.flippable.letters(
    "PyWeek 24 entry", scale=1, y=8*3, x=400, center=True,
    parent=main_screen))
all(jrti_game.flippable.letters(
    "https://pyweek.org/e/instructions/", scale=1, y=8*1, x=400, center=True,
    parent=main_screen))

jrti_game.flippable.Sprite(
    parent=main_screen,
    x=800-32-16*2, y=32,
    u=80-1, v=3*8, width=16+1, height=32+1, scale=2,
    instructions='Keyhole')

fps_display = pyglet.window.FPSDisplay(window)

pressed_keys = {}

state.tool = tool.Tool()

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

    gl.glLoadIdentity()
    gl.glPushMatrix()
    gl.glTranslatef(state.tool_x, state.tool_y, 0)
    gl.glScalef(state.tool.scale, state.tool.scale, 1)
    state.tool.draw()
    gl.glPopMatrix()

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
        finish_viewport_change()
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


@window.event
def on_key_press(sym, mod):
    try:
        key = state.keymap[sym]
    except KeyError:
        return
    if mod == 0:
        pressed_keys[key] = state.time
    if key == 'G':
        if mod == pyglet.window.key.MOD_SHIFT:
            if state.tool.name != 'grabby':
                state.tool = tool.Grabby()
        elif state.tool.name == 'grabby':
            _full_zoom()
            state.tool.grab()
    if key == 'K':
        if mod == pyglet.window.key.MOD_SHIFT:
            state.tool = tool.Key()

@window.event
def on_key_release(sym, mod):
    try:
        key = state.keymap[sym]
    except KeyError:
        return
    pressed_keys.pop(key, None)


def zoom(amount, x=None, y=None):
    state.target_zoom = clamp(state.target_zoom * 1.1 ** amount, 1, 800)

def _zoom(amount):
    cx, cy = state.center
    lx, ly = mouse_to_logical(*state.last_mouse_pos)

    old = state.zoom
    state.zoom = amount

    cx = lx - (lx - cx) * old / state.zoom
    cy = ly - (ly - cy) * old / state.zoom
    state.center = cx, cy

    finish_viewport_change()

def _full_zoom():
    if state.zoom != state.target_zoom:
        _zoom(state.target_zoom)

def finish_viewport_change():
    cx, cy = state.center
    cx = clamp(cx, 400 - 400 * state.zoom, 400 * state.zoom - 400)
    cy = clamp(cy, 300 - 300 * state.zoom, 300 * state.zoom - 300)

    state.center = cx, cy

    state.tool.deactivate()


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
    if state.zoom == state.target_zoom:
        pass
    elif 0.999 < state.zoom / state.target_zoom < 1.001:
        _zoom(state.target_zoom)
    else:
        x1 = state.zoom
        x2 = state.target_zoom
        w2 = 1 - math.exp(-dt) ** (10)
        w1 = 1 - w2
        _zoom( (x1**w1 * x2**w2) ** (1/1))
    main_screen.tick(dt)

    avg_seconds_to_bug = clamp((bug_arena.num_bugs-1/2)*4, 1, 100)
    if random.uniform(0, avg_seconds_to_bug) < dt:
        bug_arena.spawn_bug()

    tool_size = state.tool.size * state.tool.scale / 2
    tool_x = state.tool_x
    tool_y = state.tool_y
    for key, time in ((k, state.time - pressed_keys[k])
                       for k in 'OPWSAD←↑↓→'
                       if k in pressed_keys):
        dz = .1 + (time*4)**3
        dm = 2 + (time*6)**2
        if key == 'O':
            zoom(dz * dt)
        elif key == 'P':
            zoom(-dz * dt)
        elif key == 'A':
            tool_x = clamp(state.tool_x - dm, tool_size-400, 400-tool_size)
        elif key == 'D':
            tool_x = clamp(state.tool_x + dm, tool_size-400, 400-tool_size)
        elif key == 'S':
            tool_y = clamp(state.tool_y - dm, tool_size-300, 300-tool_size)
        elif key == 'W':
            tool_y = clamp(state.tool_y + dm, tool_size-300, 300-tool_size)
        elif key == '←':
            cx, cy = state.center
            cx -= dm * state.zoom * dt * 2
            state.center = cx, cy
            finish_viewport_change()
        elif key == '↑':
            cx, cy = state.center
            cy += dm * state.zoom * dt * 2
            state.center = cx, cy
            finish_viewport_change()
        elif key == '↓':
            cx, cy = state.center
            cy -= dm * state.zoom * dt * 2
            state.center = cx, cy
            finish_viewport_change()
        elif key == '→':
            cx, cy = state.center
            cx += dm * state.zoom * dt * 2
            state.center = cx, cy
            finish_viewport_change()

    if tool_x != state.tool_x or tool_y != state.tool_y:
        state.tool.speed = (tool_x - state.tool_x + tool_y - state.tool_y)
        state.tool_x = tool_x
        state.tool_y = tool_y
    else:
        state.tool.speed = 0

    state.tool.tick(dt)

def main():
    pyglet.app.run()
