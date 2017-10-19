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
    keymap={
        getattr(pyglet.window.key, k): k
        for k in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    },
)
