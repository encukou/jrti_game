import os
import pyglet
from pyglet import gl
import ctypes
import math

import jrti_game.data
from jrti_game.data import sprites
import jrti_game.flippable
import jrti_game.text
from jrti_game.bug import BugArena
from jrti_game.end import Keyhole
from jrti_game.util import clamp
from jrti_game.state import state
from jrti_game import tool
from jrti_game.coords import mouse_to_logical
from jrti_game.coords import mouse_to_main_screen

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
    margin=32,
    instructions='End',
    instructions_color=(1, 0.9, 0.5),
)
state.main_screen = main_screen
bug_arena = BugArena(
    parent=main_screen,
    x=400 - 600//2,
    y=400 - 8*32,
    width=600,
    height=8*48,
    instructions='Main Plaque',
    margin=8,
    bgcolor=(.1, .1, .1, 1)
)

all(jrti_game.text.letters(
    "Just Read the", scale=4, y=8*36, x=300, center=True, parent=bug_arena))
all(jrti_game.text.letters(
    "Instructions!", scale=8, y=8*24, x=300, center=True, parent=bug_arena))

for x in range(2):
    bug_arena.spawn_bug()

all(jrti_game.text.letters(
    "They're behind everything!", scale=2, y=8*8, x=400, center=True,
    parent=main_screen))
all(jrti_game.text.letters(
    "PyWeek 24 entry", scale=1, y=8*3, x=400, center=True,
    parent=main_screen))
all(jrti_game.text.letters(
    "https://pyweek.org/e/instructions/", scale=1, y=8*1, x=400, center=True,
    parent=main_screen))

Keyhole(
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
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER,
                       gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
                       gl.GL_LINEAR)

    gl.glFrontFace(gl.GL_CCW)
    gl.glCullFace(gl.GL_BACK)
    gl.glDisable(gl.GL_CULL_FACE)

    main_screen.draw_outer(zoom=state.zoom)
    if state.tool.grabbing:
        state.tool.grabbing.draw_grab()
    main_screen.draw_flipping(zoom=state.zoom)

    gl.glLoadIdentity()
    gl.glTranslatef(state.tool_x, state.tool_y, 0)
    gl.glScalef(state.tool.scale, state.tool.scale, 1)
    state.tool.draw()

    if state.reassign_state:
        gl.glLoadIdentity()
        time0, sym1, time1, sym2, time2 = state.reassign_state
        t0 = clamp((state.time - (time0 or state.time)) * 5, 0, 1)
        t1 = clamp((state.time - (time1 or state.time)) * 5, 0, 1)
        t2 = clamp((state.time - (time2 or state.time)) * 5, 0, 1)
        t3 = clamp((state.time - (time2 or state.time)-4/10) * 5, 0, 1)
        t4 = clamp((state.time - (time2 or state.time)-7/10) * 5, 0, 1)
        gl.glLoadIdentity()
        gl.glTranslatef(0, 8, 0)
        gl.glColor3f(0.6, 0.5, 0.4)
        size = (t0-t4) * 8
        gl.glScalef(size, size, 0)
        gl.glPushMatrix()
        gl.glRotatef(t3*180, 0, 0, 1)
        sep = t1*8
        sprites['square'].blit(-sep, -10.5, width=sep*2, height=21)
        sprites['circ3'].blit(-11.5-sep, -11.5)
        sprites['circ3'].blit(-11.5+sep, -11.5)

        gl.glColor3f(0, 0, 0)
        if sym1:
            gl.glPushMatrix()
            gl.glTranslatef(-8, 0, 0)
            gl.glScalef(t1, t1, 0)
            gl.glRotatef(-t3*180, 0, 0, 1)
            jrti_game.text.draw_key(sym1)
            gl.glPopMatrix()
        if sym2:
            gl.glPushMatrix()
            gl.glTranslatef(8, 0, 0)
            gl.glScalef(t2, t2, 0)
            gl.glRotatef(-t3*180, 0, 0, 1)
            jrti_game.text.draw_key(sym2)
            gl.glPopMatrix()
        gl.glPopMatrix()
        gl.glScalef(1/8, 1/8, 0)
        if sym1:
            jrti_game.text.draw_string(state.keymap.get(sym1, ''),
                                       center=True, x=-8*8, y=-8*5)
        if sym2:
            jrti_game.text.draw_string(state.keymap.get(sym2, ''),
                                       center=True, x=8*8, y=-8*5)

    if os.environ.get('GAME_DEBUG'):
        gl.glLoadIdentity()
        fps_display.draw()


@window.event
def on_mouse_motion(x, y, button, mod):
    state.last_mouse_pos = x, y


@window.event
def on_mouse_press(x, y, button, mod):
    main_screen.mouse_release()
    if state.ending:
        return
    if mod & pyglet.window.key.MOD_SHIFT:
        state.alt_zoom_start = [y, (x, y)]
        return
    if mod & pyglet.window.key.MOD_CTRL:
        button = pyglet.window.mouse.RIGHT
    if button == pyglet.window.mouse.LEFT:
        if not state.reassign_state:
            main_screen.mouse_press(*mouse_to_main_screen(x, y),
                                    zoom=state.zoom)
            state.tool.deactivate()
    else:
        state.last_drag_pos = x, y


@window.event
def on_mouse_drag(x, y, dx, dy, button, mod):
    if state.ending:
        return
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
        main_screen.mouse_drag(*mouse_to_main_screen(x, y), zoom=state.zoom)
    state.last_mouse_pos = x, y


@window.event
def on_mouse_release(x, y, button, mod):
    state.alt_zoom_start = None
    state.last_drag_pos = None
    main_screen.mouse_release()


@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    main_screen.mouse_release()
    if state.ending:
        return
    zoom(scroll_y, x, y)


@window.event
def on_key_press(sym, mod):
    # Apparently, some keyboards have an always-on modifier...
    # Only include the ones we care about.
    mod = mod & (pyglet.window.key.MOD_CTRL |
                 pyglet.window.key.MOD_SHIFT |
                 pyglet.window.key.MOD_ALT)

    if sym == pyglet.window.key.C and mod & pyglet.window.key.MOD_CTRL:
        raise KeyboardInterrupt()

    try:
        key = state.keymap[sym]
    except KeyError:
        key = ''

    if state.ending:
        if key in ('Exit', 'Quit'):
            exit()
        return pyglet.event.EVENT_HANDLED

    if state.reassign_state:
        main_screen.mouse_release()
        time0, sym1, time1, sym2, time2 = state.reassign_state
        if sym1 is None:
            state.reassign_state = time0, sym, state.time, None, None
        elif sym2 is None:
            state.reassign_state = time0, sym1, time1, sym, state.time
        return pyglet.event.EVENT_HANDLED

    if mod == 0:
        pressed_keys[key] = state.time

    if key in ('Exit', 'Quit'):
        exit()
    elif key == 'Grabby':
        if state.tool.name == 'grabby':
            _full_zoom()
            state.tool.grab()
        else:
            state.tool = tool.Grabby()
    elif key == 'Key':
        if state.tool.name == 'key':
            _full_zoom()
            state.tool.turn()
        else:
            state.tool = tool.Key()
    elif key == 'Reassign':
        if state.reassign_state is None:
            state.reassign_state = state.time, None, None, None, None
    elif key.startswith('Zoom '):
        try:
            level = int(key[5:])
        except ValueError:
            pass
        else:
            state.target_zoom = 1.3 ** level
    elif key == 'Cheat':
        print('Here, you cheater:', state.code)
        if mod & (pyglet.window.key.MOD_CTRL|pyglet.window.key.MOD_ALT):
            state.key_config[:] = state.code

    return pyglet.event.EVENT_HANDLED


@window.event
def on_key_release(sym, mod):
    try:
        key = state.keymap[sym]
    except KeyError:
        return
    pressed_keys.pop(key, None)


def zoom(amount, x=None, y=None):
    state.target_zoom = clamp(state.target_zoom * 1.1 ** amount,
                              state.min_zoom, 800)


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
    if state.zoom <= 1:
        cx, cy = 0, 0
    else:
        cx = clamp(cx, 400 - 400 * state.zoom, 400 * state.zoom - 400)
        cy = clamp(cy, 300 - 300 * state.zoom, 300 * state.zoom - 300)

    state.center = cx, cy

    state.tool.deactivate()


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
        w2 = 1 - math.exp(-dt) ** (10) ** state.zoom_easing
        w1 = 1 - w2
        _zoom((x1**w1 * x2**w2) ** (1/1))
    main_screen.tick(dt)

    tool_size = state.tool.size * state.tool.scale / 2
    tool_x = state.tool_x
    tool_y = state.tool_y
    for key, time in ((k, state.time - pressed_keys[k])
                      for k in pressed_keys):
        dz = .2 + (time*4)**3
        dm = clamp(2 + (time*6)**2, 0, 40)
        if key == 'Zoom Out':
            zoom(-dz * dt)
        elif key == 'Zoom In':
            zoom(dz * dt)
        elif key == 'Tool Left':
            tool_x = clamp(state.tool_x - dm, tool_size-400, 400-tool_size)
        elif key == 'Tool Right':
            tool_x = clamp(state.tool_x + dm, tool_size-400, 400-tool_size)
        elif key == 'Tool Down':
            tool_y = clamp(state.tool_y - dm, tool_size-300, 300-tool_size)
        elif key == 'Tool Up':
            tool_y = clamp(state.tool_y + dm, tool_size-300, 300-tool_size)
        elif key == 'View Left':
            cx, cy = state.center
            cx -= dm / state.zoom * dt * 15
            state.center = cx, cy
            finish_viewport_change()
        elif key == 'View Up':
            cx, cy = state.center
            cy += dm / state.zoom * dt * 15
            state.center = cx, cy
            finish_viewport_change()
        elif key == 'View Down':
            cx, cy = state.center
            cy -= dm / state.zoom * dt * 15
            state.center = cx, cy
            finish_viewport_change()
        elif key == 'View Right':
            cx, cy = state.center
            cx += dm / state.zoom * dt * 15
            state.center = cx, cy
            finish_viewport_change()

    if tool_x != state.tool_x or tool_y != state.tool_y:
        dx = tool_x - state.tool_x
        dy = tool_y - state.tool_y
        state.tool.move(dx, dy)
    else:
        state.tool.speed = 0

    if state.reassign_state:
        time0, sym1, time1, sym2, time2 = state.reassign_state
        if time2 and time2 < state.time - 9/10:
            state.keymap[sym1], state.keymap[sym2] = (
                state.keymap.get(sym2, ''), state.keymap.get(sym1, ''))
            main_screen.update_instructions()
            state.reassign_state = None

    state.tool.tick(dt)


def main():
    pyglet.app.run()
