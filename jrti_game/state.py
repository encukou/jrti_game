import types

import pyglet


state = types.SimpleNamespace(
    zoom=1,
    target_zoom=1,
    alt_zoom_start=None,
    last_drag_pos=None,
    center=[0, 0],
    last_mouse_pos=(0, 0),
    time=0,
    tool=None,
    tool_x=0,
    tool_y=0,
    reassign_state=None,
    reassign_anim_start=0,
    keymap={
        pyglet.window.key.LEFT: '←',
        pyglet.window.key.UP: '↑',
        pyglet.window.key.DOWN: '↓',
        pyglet.window.key.RIGHT: '→',
        pyglet.window.key.ESCAPE: '×',
        **{
            getattr(pyglet.window.key, k): k
            for k in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        },
        **{
            getattr(pyglet.window.key, '_' + k): k
            for k in '0123456789'
        },
    },
)
